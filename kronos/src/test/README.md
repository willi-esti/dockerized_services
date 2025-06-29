# Kronos Test Suite

This directory contains all tests for the Kronos application, organized by functionality.

## Directory Structure

```
src/test/
├── __init__.py                 # Test package initialization
├── run_tests.py               # Main test runner script
├── README.md                  # This file
├── chat/                      # Chat functionality tests
│   ├── __init__.py
│   ├── test_chat_api.py      # Chat API integration tests
│   ├── test_conversation_memory.py  # Conversation memory tests
│   ├── test_direct_responses.py     # Direct response tests
│   ├── test_greeting.py       # Greeting behavior tests
│   ├── test_markdown_chat.py  # Markdown rendering tests
│   ├── test_natural.py        # Natural conversation tests
│   ├── test_proactive.py      # Proactive conversation tests
│   ├── test_simple_requests.py # Simple request handling tests
│   └── test_specific_context.py # Context-specific tests
├── logs/                      # Logging functionality tests
│   ├── __init__.py
│   └── test_log_rotation.py   # Log rotation and management tests
├── search/                    # Search functionality tests
│   ├── __init__.py
│   └── test_search_action.py  # Search action and knowledge base tests
├── sync/                      # Synchronization tests
│   ├── __init__.py
│   └── test_sync_metadata.py  # Metadata synchronization tests
└── integration/               # Integration tests
    ├── __init__.py
    ├── test_ergo.py           # End-to-end ergo functionality test
    └── test_terms.py          # Various terms behavior test
```

## Running Tests

### Run All Tests
```bash
cd /opt/gaia/kronos/src/test
python run_tests.py
```

### Run Tests by Category
```bash
python run_tests.py --category chat         # Chat tests only
python run_tests.py --category logs         # Log tests only
python run_tests.py --category search       # Search tests only
python run_tests.py --category sync         # Sync tests only
python run_tests.py --category integration  # Integration tests only
```

### List Available Tests
```bash
python run_tests.py --list
```

### Run Individual Tests
```bash
cd /opt/gaia/kronos/src/test/chat
python test_chat_api.py
```

## Test Categories

### 🗨️ Chat Tests (`chat/`)
Tests for chat functionality including:
- API endpoints and responses
- Conversation memory and context
- Message formatting (markdown, emoji)
- Natural language processing
- Greeting and response behaviors

### 📝 Log Tests (`logs/`)
Tests for logging functionality including:
- Log rotation and compression
- Log management API endpoints
- Log retention policies
- Daily rotation schedules

### 🔍 Search Tests (`search/`)
Tests for search and knowledge base functionality including:
- Search action processing
- Knowledge base queries
- File retrieval and ranking
- Search result formatting

### 🔄 Sync Tests (`sync/`)
Tests for data synchronization including:
- Metadata synchronization
- Database sync operations
- Background task processing

### 🔗 Integration Tests (`integration/`)
End-to-end tests that span multiple modules:
- Complete workflow testing
- Cross-module interactions
- System behavior verification

## Test Requirements

All tests are designed to run against the local development environment:
- Kronos API running on `http://localhost:8000`
- All necessary services (postgres, ollama) should be running
- Use `docker-compose up` to start the full environment

## Adding New Tests

When creating new tests:
1. Place them in the appropriate category directory
2. Follow the naming convention: `test_<functionality>.py`
3. Include a test function that starts with `test_` or use `main()`
4. Add proper error handling and descriptive output
5. Update this README if adding new categories

## Best Practices

- Tests should be independent and idempotent
- Use descriptive test names and output messages
- Include both positive and negative test cases
- Test edge cases and error conditions
- Keep tests focused on specific functionality
- Use the test runner for consistency

## Troubleshooting

If tests fail:
1. Ensure all services are running (`docker-compose ps`)
2. Check service logs (`docker-compose logs kronos`)
3. Verify API endpoints are accessible
4. Check database connectivity
5. Review individual test output for specific errors
