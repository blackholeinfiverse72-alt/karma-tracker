# KarmaChain v2.1

A comprehensive karma tracking system with unified event processing, file upload support, and multi-department integration capabilities.

## Key Features

- **Unified Event Gateway**: Single endpoint for all karma operations
- **File Upload System**: Secure file upload with validation and storage
- **Event Audit Trail**: Complete event logging and lifecycle tracking
- **Docker Containerization**: Full containerized deployment with MongoDB
- **Multi-Department Support**: Analytics (BHIV), Infrastructure (Unreal), API Integration (Knowledgebase)
- **Comprehensive Testing**: Unit, integration, and file upload tests
- **Versioned API Endpoints**: Consistent API versioning for stability
- **Predictive Karma Engine**: Advanced karmic evaluation and guidance system
- **Purushartha Integration**: Actions evaluated against Dharma, Artha, Kama, Moksha principles
- **Ecosystem Hooks**: Secure API endpoints for cross-module integration
- **Advanced Token Schema**: DharmaPoints, SevaPoints, PunyaTokens, PaapTokens, DridhaKarma, AdridhaKarma, SanchitaKarma, PrarabdhaKarma, Rnanubandhan
- **Q-Learning Integration**: Adaptive karma prediction and atonement recommendations
- **Comprehensive Observability**: Structured logging, metrics, and audit trails
- **Input Validation**: Robust validation for all API endpoints
- **Stress Testing**: Performance testing for 100+ concurrent users

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```
3. Start the application:
   ```
   docker-compose up -d
   ```
4. Access the API at `http://localhost:8000`
5. View API documentation at `http://localhost:8000/docs`

### Manual Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Start the application:
   ```
   uvicorn main:app --reload
   ```

## API Documentation

- [API Documentation](docs/api_documentation.md) - Complete API reference
- [Unified Event API](docs/unified_event_api.md) - Unified event gateway guide
- [KarmaChain v2 Guide](docs/karmachain_v2.md) - System overview and architecture
- [Handover Guide](docs/HANDOVER_GUIDE.md) - Deployment and integration guide
- [Karma API Endpoints](docs/karma_api_endpoints.md) - Ecosystem hooks and integration guide

## Testing & Validation

### Integration Tests
Run integration tests to verify system functionality:

```bash
# Using the provided test script
python tests/integration_demo.py

# Or using the Docker setup script
./scripts/run_local.sh

# Test the new karma API endpoints
python tests/test_karma_api.py
```

### Stress Testing
Test system performance with 100+ concurrent users:

```bash
# Run comprehensive stress test
python tests/stress_test.py

# View stress test results
cat stress_test_results.json
```

### Input Validation Testing
Validate input sanitization and error handling:

```bash
# Test validation middleware
python -c "from validation import *; test_validation()"

# Check validation logs
tail -f logs/validation.log
```

### Observability & Monitoring
Access comprehensive system metrics and logs:

```bash
# View API logs
tail -f logs/api.log

# Check error logs
tail -f logs/errors.log

# Monitor audit trail
tail -f logs/audit.log

# Export audit trail for analysis
python -c "from observability import karmachain_logger; karmachain_logger.export_audit_trail('audit_export.json')"
```

## System Status

✅ **Production Ready** - System is fully implemented, tested, and ready for production deployment

### Core Features Status
- Unified Event Gateway: ✅ Implemented
- File Upload System: ✅ Implemented  
- Event Audit Trail: ✅ Implemented
- Docker Environment: ✅ Implemented
- Multi-Department Support: ✅ Implemented
- Comprehensive Testing: ✅ Implemented
- Predictive Karma Engine: ✅ Implemented
- Purushartha Integration: ✅ Implemented
- Ecosystem Hooks: ✅ Implemented

### Day 5 Enhancements
- Advanced Token Schema: ✅ Implemented
- Q-Learning Integration: ✅ Implemented
- Input Validation: ✅ Implemented
- Observability & Logging: ✅ Implemented
- Stress Testing: ✅ Implemented
- Production Hardening: ✅ Implemented

## Integration Guide

### Unified Event Gateway

The recommended way to integrate with KarmaChain is through the unified event gateway:

```
POST /v1/karma/event
{
  "event_type": "life_event",
  "user_id": "user123",
  "data": {
    "role": "human",
    "action": "help",
    "description": "Helped a colleague with debugging"
  }
}
```

### Ecosystem Hooks

For direct integration with specific modules, use the karma API endpoints:

```
GET /api/v1/karma/{user_id}              # Get full karma profile
POST /api/v1/log-action/                 # Log user action
POST /api/v1/submit-atonement/           # Submit atonement completion
```

These endpoints provide module-specific scores for Finance, InsightFlow, Gurukul, and Game.

### File Upload Support

Upload files as evidence for atonement events:

```
POST /v1/karma/event/with-file
Form Data:
  - event_data: JSON string with event details
  - file: Upload file (jpg, jpeg, png, pdf, doc, docx)
```

### Supported Event Types

- `life_event`: Log karma actions and behaviors
- `appeal`: Submit karma appeals
- `atonement`: Request and complete atonement plans
- `atonement_with_file`: Atonement with supporting evidence files
- `death_event`: Record death events for karma transfer
- `stats_request`: Query user karma statistics

## Token Schema & Scoring System

### Advanced Karma Tokens

The system implements a comprehensive token schema based on Vedic principles:

#### Primary Tokens
- **DharmaPoints**: Righteous action points based on dharma compliance
- **SevaPoints**: Service and selfless action points
- **PunyaTokens**: Merit tokens for virtuous actions
- **PaapTokens**: Demerit tokens with severity levels (1-10)

#### Karma Types
- **DridhaKarma**: Fixed karma that must be experienced
- **AdridhaKarma**: Flexible karma that can be modified
- **SanchitaKarma**: Accumulated karma from past actions
- **PrarabdhaKarma**: Karma currently being experienced
- **Rnanubandhan**: Karmic debt relationships

### Purushartha Scoring

Actions are evaluated against the four Purushartha principles:

#### Dharma (Righteousness)
- Compliance with moral and ethical duties
- Adherence to universal laws and principles
- Impact on spiritual growth and liberation

#### Artha (Prosperity)
- Material and spiritual wealth generation
- Resource utilization efficiency
- Contribution to collective prosperity

#### Kama (Desire)
- Fulfillment of legitimate desires
- Balance between desire and restraint
- Impact on overall well-being

#### Moksha (Liberation)
- Progress toward spiritual liberation
- Reduction of karmic bonds
- Advancement on the path to enlightenment

### Q-Learning Integration

The system uses Q-learning algorithms to:
- Predict karmic outcomes based on user patterns
- Recommend optimal atonement plans
- Adapt scoring based on user behavior
- Provide personalized spiritual guidance

### Atonement System

Comprehensive atonement framework with three pillars:

#### Daan (Charity)
- Material donations and charitable acts
- Service to others and community support
- Resource sharing and generosity

#### Bhakti (Devotion)
- Spiritual practices and devotion
- Meditation, prayer, and ritual observance
- Cultivation of divine connection

#### Tap (Austerity)
- Self-discipline and penance
- Fasting and physical purification
- Mental and spiritual austerity practices

Each atonement type has specific units and effectiveness ratings based on the severity of PaapTokens being addressed.

## Directory Structure

```
├── data/                  # Data files and vedic corpus
├── docs/                  # API documentation and guides
├── routes/                # API routes
│   └── v1/                # Version 1 API
│       └── karma/         # Karma-related endpoints
├── utils/                 # Utility functions (atonement, merit, paap, etc.)
├── scripts/               # Setup and utility scripts
├── tests/                 # Integration and unit tests
├── uploads/               # File upload storage
├── backups/               # System backups
├── logs/                  # Application logs
├── mongo-init/            # MongoDB initialization scripts
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── main.py                # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── system_manifest.json   # System configuration and status
```

## License

Proprietary - All rights reserved