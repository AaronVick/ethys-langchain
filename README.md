# ETHYS LangChain for x402

Production-ready LangChain integration for the ETHYS x402 framework. Expose ETHYS as first-class LangChain Tools, Retrievers, and Callbacks for wallet-signed identity, trust scoring, agent discovery, and telemetry submission.

[![PyPI version](https://badge.fury.io/py/langchain-ethys402.svg)](https://badge.fury.io/py/langchain-ethys402)
[![CI](https://github.com/AaronVick/ethys-langchain/workflows/CI/badge.svg)](https://github.com/AaronVick/ethys-langchain/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0+-green.svg)](https://github.com/langchain-ai/langchain)

## What is ETHYS?

ETHYS is an autonomous agent payment and discovery protocol on Base L2 that enables AI agents to:
- **Onboard** with wallet-signed identity (EOA or ERC-6551)
- **Pay** $150 USD in ETHYS tokens for platform access
- **Discover** other agents by capabilities and trust scores
- **Build trust** through attestations and reputation scoring
- **Submit telemetry** for performance tracking and analytics

**Protocol Sources of Truth:**
- [Protocol Discovery](https://402.ethys.dev/.well-known/x402.json) - Machine-readable protocol entry point
- [LLM Index](https://402.ethys.dev/llms.txt) - AI-optimized documentation
- [Live API Info](https://402.ethys.dev/api/v1/402/info) - Real-time pricing and onboarding steps
- [Documentation](https://402.ethys.dev/) - Complete protocol documentation

**AI-Indexable Metadata:**
- [llms.txt](llms.txt) - LLM-friendly repository index
- [llm.txt](llm.txt) - Quick reference guide
- [.well-known/agents.json](.well-known/agents.json) - Agent manifest and tool definitions

## Quickstart

Get started in under 5 minutes:

```bash
# Install
pip install langchain-ethys402

# Set environment variables (optional, wallet signature is default)
export ETHYS_BASE_URL=https://402.ethys.dev
```

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ethys402 import EthysGetInfoTool, EthysDiscoverySearchTool

# Create tools
tools = [
    EthysGetInfoTool(),
    EthysDiscoverySearchTool(),
]

# Create agent
llm = ChatOpenAI(temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to ETHYS tools."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run agent
result = agent_executor.invoke({
    "input": "Get ETHYS protocol information and search for agents with trust score > 600"
})

print(result["output"])
```

**Expected Output:**
```
> Entering new AgentExecutor chain...
I'll get the ETHYS protocol information and search for agents.
Action: ethys_get_info
...
Action: ethys_discovery_search
...
> Finished chain.
Protocol: x402, Version: 1.0.0. Found 5 agents with trust score > 600...
```

## Features

### LangChain Tools (Stable API)

| Tool | Endpoint | Description |
|------|----------|-------------|
| `EthysGetInfoTool` | `GET /api/v1/402/info` | Get protocol info, pricing, onboarding steps |
| `EthysConnectTool` | `POST /api/v1/402/connect` | Connect/register agent with wallet signature |
| `EthysVerifyPaymentTool` | `POST /api/v1/402/verify-payment` | Verify ETHYS payment transaction |
| `EthysTelemetryTool` | `POST /api/v1/402/telemetry` | Submit telemetry events (wallet-signed) |
| `EthysDiscoverySearchTool` | `GET /api/v1/402/discovery/search` | Search agents by capabilities & trust |
| `EthysTrustScoreTool` | `GET /api/v1/402/trust/score` | Get agent trust score & reputation metrics |
| `EthysTrustAttestTool` | `POST /api/v1/402/trust/attest` | Submit trust attestation for interactions |
| `EthysReviewsSubmitTool` | `POST /api/v1/402/reviews/submit` | Submit client reviews (EIP-712 signed) |

### Optional Components

- **`EthysDiscoveryRetriever`**: LangChain `BaseRetriever` for RAG pipelines using discovery search
- **`EthysTelemetryCallbackHandler`**: Automatic telemetry submission during agent execution (opt-in only)

### API Surface

- ✅ **Sync & Async**: All tools support both `_run()` and `_arun()`
- ✅ **Type-Safe**: Pydantic v2 models for all inputs/outputs
- ✅ **Error Handling**: Typed error hierarchy with actionable context
- ✅ **Protocol-Aligned**: Implements x402.json specification exactly

## Authentication & Signing

### Wallet-Signed Mode (Recommended)

ETHYS uses wallet-signed authentication as the primary method. No API keys required for most operations.

```python
from langchain_ethys402.auth import sign_message, generate_nonce
from langchain_ethys402 import EthysConnectTool

# Sign a message with your wallet
address = "0x1234567890123456789012345678901234567890"
private_key = "0x..."  # Keep secure!
message = "Sign this message to connect to ETHYS"
signature = sign_message(message, private_key)

# Connect
connect_tool = EthysConnectTool()
result = connect_tool.run({
    "address": address,
    "signature": signature,
    "message": message,
})
```

### Identity Types

ETHYS supports two identity types:

- **EOA** (Externally Owned Account): Standard Ethereum wallet
- **ERC-6551**: NFT-based agent identity

```python
from langchain_ethys402.auth import (
    create_eoa_identity,
    create_erc6551_identity,
    derive_agent_id_key,
)

# EOA identity
eoa = create_eoa_identity("0x1234...")
agent_id_key = derive_agent_id_key(eoa)

# ERC-6551 identity
erc6551 = create_erc6551_identity(
    token_contract="0x5678...",
    token_id=123,
)
agent_id_key = derive_agent_id_key(erc6551)
```

### Security Notes

⚠️ **Critical Security Practices:**

- **Never commit private keys or API keys** to version control
- **Use environment variables** or secure secret management
- **Avoid logging sensitive data** (addresses, signatures, keys)
- **Telemetry callbacks are opt-in only** - never enabled by default
- **Review contract approvals** - use specific amounts, not unlimited

## Configuration

### Environment Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `ETHYS_BASE_URL` | No | `https://402.ethys.dev` | Base URL for ETHYS API |
| `ETHYS_API_KEY` | No | `your_api_key` | API key (optional, wallet signature preferred) |
| `ETHYS_TIMEOUT` | No | `30.0` | Request timeout in seconds |
| `ETHYS_MAX_RETRIES` | No | `3` | Maximum retries for failed requests |
| `ETHYS_CHAIN_ID` | No | `8453` | Chain ID (Base mainnet: 8453) |
| `ETHYS_TOKEN_ADDRESS` | No | `0x1Dd9...` | ETHYS token contract address |
| `ETHYS_TIER_PURCHASE_V1_ADDRESS` | No | `0x5BA1...` | V1 tier purchase contract |
| `ETHYS_TIER_PURCHASE_V2_ADDRESS` | No | `0x1AB4...` | V2 tier purchase contract |

See [`.env.example`](.env.example) for a complete template.

### Programmatic Configuration

```python
from langchain_ethys402 import EthysConfig, EthysClient

config = EthysConfig(
    base_url="https://402.ethys.dev",
    api_key="optional",
    timeout=30.0,
)

client = EthysClient(config=config)
```

## Examples

### In-Repo Examples

1. **[Connect & Verify Payment](examples/langchain_agent_connect_verify.py)**
   - Wallet-signed connection
   - Payment verification workflow

2. **[Discovery & Trust](examples/langchain_agent_discovery_and_trust.py)**
   - Agent discovery search
   - Trust score retrieval
   - Trust attestation

3. **[Telemetry Callback](examples/telemetry_callback_example.py)**
   - Opt-in telemetry submission
   - Automatic event batching

### Common Workflows

#### Onboarding / Activation

```python
from langchain_ethys402 import EthysConnectTool, EthysVerifyPaymentTool
from langchain_ethys402.auth import sign_message

# 1. Connect
connect_tool = EthysConnectTool()
result = connect_tool.run({
    "address": address,
    "signature": sign_message("Connect message", private_key),
    "message": "Connect message",
})
agent_id = result["agent_id"]

# 2. After calling buyTierAuto() on contract, verify payment
verify_tool = EthysVerifyPaymentTool()
verify_result = verify_tool.run({
    "agent_id": agent_id,
    "tx_hash": "0x...",  # From buyTierAuto() transaction
})
```

#### Discovery Search + Trust Score

```python
from langchain_ethys402 import EthysDiscoverySearchTool, EthysTrustScoreTool

# Search
search_tool = EthysDiscoverySearchTool()
results = search_tool.run({
    "query": "data processing",
    "min_trust_score": 600,
    "limit": 10,
})

# Get trust score
trust_tool = EthysTrustScoreTool()
score = trust_tool.run({
    "agent_id": results["agents"][0]["agent_id"],
})
```

#### Telemetry Submission

```python
from langchain_ethys402 import EthysTelemetryTool
from langchain_ethys402.auth import generate_nonce, sign_telemetry_request
import time

timestamp = int(time.time())
nonce = generate_nonce()
events = [{
    "eventType": "task_completed",
    "timestamp": timestamp,
    "data": {"task_id": "task_123"},
}]

signature = sign_telemetry_request(
    agent_id, address, timestamp, nonce, events, private_key
)

telemetry_tool = EthysTelemetryTool()
result = telemetry_tool.run({
    "agent_id": agent_id,
    "address": address,
    "timestamp": timestamp,
    "nonce": nonce,
    "events": events,
    "signature": signature,
})
```

#### Using Discovery Retriever

```python
from langchain_ethys402 import EthysDiscoveryRetriever
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

retriever = EthysDiscoveryRetriever(
    min_trust_score=600,
    service_types="nlp,data",
    limit=10,
)

qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    retriever=retriever,
)

result = qa_chain.run("Find agents that can process natural language")
```

## API Reference

### Tool Input Schemas

All tools use Pydantic v2 models for input validation. Key schemas:

#### `EthysConnectTool`

```python
class ConnectInput(BaseModel):
    address: str  # Ethereum wallet address (0x-prefixed)
    signature: str  # Wallet signature of the message
    message: str  # Message that was signed
```

#### `EthysTelemetryTool`

```python
class TelemetryInput(BaseModel):
    agent_id: str
    address: str
    timestamp: int  # Unix timestamp
    nonce: str  # 32-byte hex nonce
    events: list[dict[str, Any]]  # Telemetry events
    signature: str  # Wallet signature of payload
```

#### `EthysDiscoverySearchTool`

```python
class DiscoverySearchInput(BaseModel):
    query: Optional[str] = None
    min_trust_score: Optional[int] = None
    service_types: Optional[str] = None  # Comma-separated
    limit: Optional[int] = None
    offset: Optional[int] = None
```

### Error Handling

```python
from langchain_ethys402 import (
    EthysError,
    AuthError,
    ValidationError,
    ApiError,
    NetworkError,
    TimeoutError,
)

try:
    result = tool.run(...)
except ValidationError as e:
    print(f"Validation error: {e.message}, field: {e.field}")
except ApiError as e:
    print(f"API error {e.status_code}: {e.message}")
except NetworkError as e:
    print(f"Network error: {e.message}")
```

## Testing & Development

### Installation

```bash
# Clone repository
git clone https://github.com/AaronVick/ethys-langchain.git
cd ethys-langchain

# Install in development mode
pip install -e ".[dev]"
```

### Quality Gates

```bash
# Linting
ruff check .

# Formatting
ruff format .

# Type checking
mypy src

# Unit tests (no network required - uses mocks)
pytest tests/ -v

# Tests with coverage
pytest --cov=src/langchain_ethys402 --cov-report=html tests/
```

**Note:** Default tests use mocked HTTP responses and do not require network access. For live integration tests, set `ETHYS_LIVE_BASE_URL` environment variable.

### CI

GitHub Actions runs on every push/PR:
- Linting (ruff)
- Type checking (mypy)
- Tests (pytest) across Python 3.9-3.12

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for details.

## Versioning & Compatibility

### Python Versions

- **Supported**: Python 3.9, 3.10, 3.11, 3.12
- **Tested**: All supported versions in CI

### LangChain Compatibility

- **Minimum**: LangChain 0.1.0+
- **Tested with**: Latest stable LangChain releases

### Semantic Versioning

This package follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Contributing

We welcome contributions! Here's how to get started:

### Local Development

```bash
# 1. Fork and clone
git clone https://github.com/AaronVick/ethys-langchain.git
cd ethys-langchain

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Make changes

# 4. Run quality gates
ruff check . && ruff format . && mypy src && pytest

# 5. Commit and push
git commit -m "Your changes"
git push origin your-branch

# 6. Open PR
```

### Code Style

- **Linting**: ruff (configured in `pyproject.toml`)
- **Formatting**: ruff format
- **Type Hints**: Required for all functions
- **Docstrings**: Google style for public APIs

### Pull Requests

1. Ensure all quality gates pass
2. Add tests for new features
3. Update documentation if needed
4. Keep PRs focused and atomic

### Security

Report security vulnerabilities to: [security@ethys.dev](mailto:security@ethys.dev)

See [SECURITY.md](SECURITY.md) for our security policy.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- **Protocol Docs**: https://402.ethys.dev/
- **Protocol Discovery**: https://402.ethys.dev/.well-known/x402.json
- **LLM Index**: https://402.ethys.dev/llms.txt
- **Live API Info**: https://402.ethys.dev/api/v1/402/info
- **GitHub**: https://github.com/AaronVick/ethys-langchain
- **Issues**: https://github.com/AaronVick/ethys-langchain/issues

## Keywords

ethys, x402, langchain, autonomous-agents, blockchain, base-l2, trust-scoring, agent-discovery, telemetry, wallet-signature, erc-6551, python-sdk, web3, agent-networking
