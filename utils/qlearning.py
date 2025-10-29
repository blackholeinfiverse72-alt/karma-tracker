import datetime
import numpy as np
from config import ACTIONS, ROLE_SEQUENCE, ALPHA, GAMMA, REWARD_MAP, CHEAT_PUNISHMENT_LEVELS, ATONEMENT_REWARDS
from utils.merit import determine_role_from_merit

states = ROLE_SEQUENCE[:]
n_states = len(states)
n_actions = len(ACTIONS)
Q = np.zeros((n_states, n_actions))

# Lazy database connection - will be initialized on first use
db_initialized = False
qtable_col = None
users_col = None

def initialize_db():
    """Initialize database connections lazily"""
    global db_initialized, qtable_col, users_col, Q
    if db_initialized:
        return
    
    try:
        from database import qtable_col as qtable_collection, users_col as users_collection
        qtable_col = qtable_collection
        users_col = users_collection
        
        # restore Q-table from DB
        q_doc = qtable_col.find_one({})
        if q_doc and "q" in q_doc:
            try:
                Q = np.array(q_doc["q"])
                # Ensure Q-table has the correct shape
                if Q.shape != (n_states, n_actions):
                    print(f"DEBUG: Q-table shape mismatch. Expected {(n_states, n_actions)}, got {Q.shape}. Resetting.")
                    Q = np.zeros((n_states, n_actions))
            except Exception as e:
                print(f"DEBUG: Error restoring Q-table: {e}. Resetting.")
                Q = np.zeros((n_states, n_actions))
        else:
            print(f"DEBUG: No Q-table found in DB. Creating new one with shape {(n_states, n_actions)}")
            Q = np.zeros((n_states, n_actions))
        
        db_initialized = True
    except Exception as e:
        print(f"WARNING: Could not initialize database for Q-learning: {e}")
        # Continue without DB - will use in-memory Q-table only
        db_initialized = False

def save_q_table():
    """Save Q-table to database if available"""
    if not db_initialized or qtable_col is None:
        return  # Skip saving if DB not available
    try:
        # Use timezone-aware datetime (fix for Python 3.12+)
        qtable_col.replace_one({}, {"q": Q.tolist(), "updated_at": datetime.datetime.now(datetime.timezone.utc)}, upsert=True)
    except Exception as e:
        print(f"WARNING: Could not save Q-table: {e}")

def q_learning_step(user_id: str, state: str, action: str, reward: float):
    initialize_db()  # Ensure database is initialized
    print(f"DEBUG q_learning_step: user_id={user_id}, state={state}, action={action}, reward={reward}")
    
    if not db_initialized or users_col is None:
        print(f"WARNING: Database not available, skipping Q-learning update")
        return reward, state
    
    # Ensure state is valid
    if state not in states:
        state = states[0]  # Default to first state if invalid
    s = states.index(state)
    print(f"DEBUG: state={state}, s={s}")
    
    # Ensure action is valid
    if action not in ACTIONS:
        # Handle unknown action gracefully
        print(f"DEBUG: action {action} not in ACTIONS")
        return reward, state
    a = ACTIONS.index(action)
    print(f"DEBUG: action={action}, a={a}")

    user_doc = users_col.find_one({"user_id": user_id})
    if not user_doc:
        print(f"DEBUG: user {user_id} not found")
        return reward, state

    print(f"DEBUG: user_doc={user_doc}")
    print(f"DEBUG: user_doc.balances type={type(user_doc.get('balances'))}")
    print(f"DEBUG: user_doc.balances={user_doc.get('balances')}")
    
    temp_balances = user_doc["balances"].copy()
    print(f"DEBUG: temp_balances={temp_balances}")
    
    # Get the appropriate token for the action
    if action == "cheat":
        # For cheat actions, we'll use DharmaPoints as the token (as defined in CHEAT_PUNISHMENT_LEVELS)
        token = "DharmaPoints"
    else:
        # For regular actions, use the token defined in REWARD_MAP
        if action in REWARD_MAP:
            token = REWARD_MAP[action]["token"]
        else:
            # Default token if action not found
            token = "DharmaPoints"
    
    print(f"DEBUG: token={token}")
    
    # Update the correct token balance
    current_balance = temp_balances.get(token, 0)
    # Ensure the current balance is a number, not a dict
    if isinstance(current_balance, dict):
        current_balance = 0
    temp_balances[token] = current_balance + reward
    print(f"DEBUG: current_balance={current_balance}, new balance={temp_balances[token]}")

    estimated_merit = temp_balances.get("DharmaPoints", 0) * 1.0 + temp_balances.get("SevaPoints", 0) * 1.2 + temp_balances.get("PunyaTokens", 0) * 3.0
    print(f"DEBUG: estimated_merit={estimated_merit}")
    next_role = determine_role_from_merit(estimated_merit)
    print(f"DEBUG: next_role={next_role}")
    
    # Check if next_role is in states before calling index
    if next_role not in states:
        print(f"DEBUG: next_role {next_role} not in states {states}")
        next_state = 0  # Default to first state
    else:
        next_state = states.index(next_role)
    print(f"DEBUG: next_state={next_state}")

    print(f"DEBUG: Q.shape={Q.shape}, s={s}, a={a}, next_state={next_state}")
    Q[s, a] = Q[s, a] + ALPHA * (reward + GAMMA * float(np.max(Q[next_state])) - Q[s, a])
    save_q_table()
    
    # Return the reward and the next role as expected
    return reward, next_role

def atonement_q_learning_step(user_id: str, severity_class: str):
    """
    Apply Q-learning update for atonement completion.
    
    Args:
        user_id (str): The user's ID
        severity_class (str): The severity class of the completed atonement
        
    Returns:
        tuple: (reward_value, next_role)
    """
    initialize_db()  # Ensure database is initialized
    
    if not db_initialized or users_col is None:
        print(f"WARNING: Database not available, skipping atonement Q-learning update")
        return 0, None
    
    # Get user and current state
    user_doc = users_col.find_one({"user_id": user_id})
    if not user_doc:
        return 0, None
    
    state = user_doc.get("role", states[0])
    if state not in states:
        state = states[0]
    
    s = states.index(state)
    
    # Get reward for atonement completion
    if severity_class not in ATONEMENT_REWARDS:
        return 0, state
    
    reward_info = ATONEMENT_REWARDS[severity_class]
    reward_value = reward_info["value"]
    token = reward_info["token"]
    
    # Update user's balances
    temp_balances = user_doc["balances"].copy()
    
    # Handle nested PaapTokens structure
    if token.startswith("PaapTokens."):
        # Extract the severity class from token (e.g., "PaapTokens.minor" -> "minor")
        paap_severity = token.split(".")[1]
        if "PaapTokens" not in temp_balances:
            temp_balances["PaapTokens"] = {}
        if paap_severity not in temp_balances["PaapTokens"]:
            temp_balances["PaapTokens"][paap_severity] = 0
        temp_balances["PaapTokens"][paap_severity] += reward_value
    else:
        # Handle regular tokens
        temp_balances[token] = temp_balances.get(token, 0) + reward_value
    
    # Calculate next state based on updated balances
    estimated_merit = temp_balances.get("DharmaPoints", 0) * 1.0 + temp_balances.get("SevaPoints", 0) * 1.2 + temp_balances.get("PunyaTokens", 0) * 3.0
    next_role = determine_role_from_merit(estimated_merit)
    next_state = states.index(next_role)
    
    # Choose a representative action for atonement (using "helping_peers" as it's a positive action)
    atonement_action = "helping_peers"
    if atonement_action in ACTIONS:
        a = ACTIONS.index(atonement_action)
        
        # Update Q-table with positive reinforcement for atonement
        Q[s, a] = Q[s, a] + ALPHA * (reward_value + GAMMA * float(np.max(Q[next_state])) - Q[s, a])
        save_q_table()
    
    # Update user's balance with the reward
    if token.startswith("PaapTokens."):
        # Handle nested PaapTokens structure
        paap_severity = token.split(".")[1]
        users_col.update_one(
            {"user_id": user_id},
            {"$inc": {f"balances.PaapTokens.{paap_severity}": reward_value}}
        )
    else:
        # Handle regular tokens
        users_col.update_one(
            {"user_id": user_id},
            {"$inc": {f"balances.{token}": reward_value}}
        )
    
    return reward_value, next_role