# API Specifications

This directory contains all specifications for the Neo4j Multi-Database REST API.

## 📋 Specification Files

### Core Specifications
- **[api-overview.md](./api-overview.md)** - High-level API overview and design principles
- **[endpoints-health.md](./endpoints-health.md)** - Health and metadata endpoints
- **[endpoints-search.md](./endpoints-search.md)** - Search endpoints specification
- **[endpoints-query.md](./endpoints-query.md)** - Query execution endpoints
- **[endpoints-nodes.md](./endpoints-nodes.md)** - Node operation endpoints
- **[endpoints-schema.md](./endpoints-schema.md)** - Schema endpoints
- **[authentication.md](./authentication.md)** - Authentication and security
- **[error-handling.md](./error-handling.md)** - Error response specifications
- **[data-models.md](./data-models.md)** - Request/response data models

### Examples
- **[examples/](./examples/)** - Concrete request/response examples

### Architecture Decisions
- **[adrs/](./adrs/)** - Architecture Decision Records

### Test Scenarios
- **[test-scenarios/](./test-scenarios/)** - Detailed test scenarios

## 🔄 Specification-Driven Development Process

1. **Write Specifications First** - Define API behavior before implementation
2. **Review Specifications** - Team reviews and approves specs
3. **Write Tests** - Create tests based on specifications
4. **Implement** - Write code to pass tests and match specs
5. **Validate** - Ensure implementation matches specifications
6. **Update** - Keep specs synchronized with implementation

## 📝 How to Use These Specs

### For Developers
1. Read the relevant specification file
2. Understand expected behavior
3. Write tests based on spec
4. Implement to match spec
5. Validate implementation

### For Reviewers
1. Check if implementation matches spec
2. Verify all spec requirements are met
3. Ensure error cases are handled

### For Frontend Developers
1. Use specs to understand API contracts
2. Reference examples for request/response formats
3. Implement client code based on specs

## 🚀 Getting Started

1. Start with **[api-overview.md](./api-overview.md)** for general understanding
2. Read endpoint specs for features you're implementing
3. Check **[data-models.md](./data-models.md)** for request/response structures
4. Review **[examples/](./examples/)** for concrete usage
5. Check **[adrs/](./adrs/)** for architectural context

## ✅ Checklist: Adding a New Endpoint

- [ ] Add endpoint spec to appropriate `endpoints-*.md` file
- [ ] Define request/response models in `data-models.md`
- [ ] Add error cases to `error-handling.md`
- [ ] Create examples in `examples/`
- [ ] Write test scenarios in `test-scenarios/`
- [ ] Get spec reviewed and approved
- [ ] Write tests based on spec
- [ ] Implement endpoint
- [ ] Validate against spec
