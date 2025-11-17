# TOON Response Format

TOON (Token-Oriented Object Notation) is an LLM-optimized serialization format that provides a more compact and readable alternative to JSON for tool responses. When enabled, TOON reduces token usage by approximately 30-60% compared to equivalent JSON representations, making it ideal for AI agent interactions with the Itential Platform.

## Overview

The Itential MCP server supports two response serialization formats:

- **JSON** (default): Standard JSON format for maximum compatibility
- **TOON**: LLM-optimized format for improved token efficiency and readability

TOON is designed specifically for Large Language Model consumption, using a human-readable structure that eliminates unnecessary syntax while preserving data structure and relationships.

## Key Features

TOON provides several advantages over traditional JSON:

1. **Token Reduction**: 30-60% fewer tokens compared to JSON
2. **Improved Readability**: Cleaner structure without excessive punctuation
3. **Indentation-Based Structure**: Visual hierarchy through whitespace
4. **Tabular Arrays**: Efficient representation of uniform data sets
5. **Backward Compatible**: Can be used alongside JSON without breaking changes

## TOON Format Specifications

### Basic Structure

TOON uses the following conventions:

- **Key-Value Pairs**: Uses colons for separation (e.g., `name: router-01`)
- **No Quotes**: Eliminates quotation marks around strings and keys
- **No Braces**: Removes `{}` and uses indentation for structure
- **Array Lengths**: Square brackets indicate array sizes (e.g., `[2]`)
- **Indentation**: 2 spaces per level for nested structures

### Object Serialization

Objects are represented with key-value pairs, one per line:

**JSON Format:**
```json
{
  "name": "router-01",
  "host": "192.168.1.1",
  "deviceType": "cisco_ios",
  "status": "active"
}
```

**TOON Format:**
```
name: router-01
host: 192.168.1.1
deviceType: cisco_ios
status: active
```

### Nested Objects

Nested structures use indentation to show hierarchy:

**JSON Format:**
```json
{
  "device": {
    "name": "router-01",
    "location": {
      "site": "datacenter-west",
      "rack": "A-12"
    }
  }
}
```

**TOON Format:**
```
device:
  name: router-01
  location:
    site: datacenter-west
    rack: A-12
```

### Array Serialization

Arrays with uniform structure use a compact tabular format:

**JSON Format:**
```json
[
  {"id": 1, "name": "Alice", "email": "alice@example.com"},
  {"id": 2, "name": "Bob", "email": "bob@example.com"}
]
```

**TOON Format:**
```
[2]{id,name,email}:
1,Alice,alice@example.com
2,Bob,bob@example.com
```

The format `[2]{id,name,email}:` indicates:
- `[2]`: Array contains 2 items
- `{id,name,email}`: Column headers
- `:`: Separator before data rows

### Mixed Arrays

Arrays with non-uniform structure maintain object notation:

**JSON Format:**
```json
[
  {"type": "router", "count": 5},
  {"type": "switch", "count": 12, "vendor": "cisco"}
]
```

**TOON Format:**
```
[2]:
  type: router
  count: 5
  ---
  type: switch
  count: 12
  vendor: cisco
```

## Configuration

### Server Configuration

Enable TOON format using any of these methods:

**1. Command Line:**
```bash
itential-mcp --response-format toon
```

**2. Environment Variable:**
```bash
export ITENTIAL_MCP_SERVER_RESPONSE_FORMAT=toon
itential-mcp
```

**3. Configuration File:**
```ini
[server]
response_format = toon
```

### Returning to JSON Format

To revert to JSON format, simply change the configuration:

```bash
itential-mcp --response-format json
```

Or omit the configuration option entirely (JSON is the default).

## Use Cases

### When to Use TOON

TOON is particularly effective for:

- **Large Data Sets**: Device inventories, configuration lists, job metrics
- **Tabular Data**: Arrays of similar objects with consistent schemas
- **Nested Structures**: Complex hierarchical data like compliance reports
- **Frequent API Calls**: Reducing token costs for high-volume operations
- **AI Agent Interactions**: Improving LLM comprehension and response generation

### When to Use JSON

JSON may be preferred for:

- **Integration with Existing Tools**: Systems expecting standard JSON
- **API Testing**: Using tools like curl or Postman
- **Debugging**: Familiarity with JSON syntax
- **Compatibility Requirements**: Strict JSON parsing requirements

## Examples

### Device Configuration Example

**Tool Call:** `get_devices`

**JSON Response (148 tokens):**
```json
[
  {
    "id": "dev-001",
    "name": "core-router-01",
    "host": "192.168.1.1",
    "deviceType": "cisco_ios",
    "status": "active",
    "lastBackup": "2025-01-15T10:30:00Z"
  },
  {
    "id": "dev-002",
    "name": "core-router-02",
    "host": "192.168.1.2",
    "deviceType": "cisco_ios",
    "status": "active",
    "lastBackup": "2025-01-15T10:35:00Z"
  }
]
```

**TOON Response (92 tokens - 38% reduction):**
```
[2]{id,name,host,deviceType,status,lastBackup}:
dev-001,core-router-01,192.168.1.1,cisco_ios,active,2025-01-15T10:30:00Z
dev-002,core-router-02,192.168.1.2,cisco_ios,active,2025-01-15T10:35:00Z
```

### Workflow Job Example

**Tool Call:** `describe_job`

**JSON Response (185 tokens):**
```json
{
  "id": "job-12345",
  "workflow": "Device Provisioning",
  "status": "completed",
  "startTime": "2025-01-15T14:20:00Z",
  "endTime": "2025-01-15T14:22:30Z",
  "duration": 150,
  "tasks": [
    {
      "name": "Validate Device",
      "status": "success",
      "duration": 45
    },
    {
      "name": "Apply Configuration",
      "status": "success",
      "duration": 90
    }
  ]
}
```

**TOON Response (118 tokens - 36% reduction):**
```
id: job-12345
workflow: Device Provisioning
status: completed
startTime: 2025-01-15T14:20:00Z
endTime: 2025-01-15T14:22:30Z
duration: 150
tasks[2]{name,status,duration}:
Validate Device,success,45
Apply Configuration,success,90
```

## Implementation Details

### Middleware Architecture

The TOON serialization is implemented as FastMCP middleware that:

1. Intercepts tool call responses
2. Detects the configured response format
3. Applies appropriate serialization
4. Returns formatted response to the client

The middleware operates transparently without requiring changes to individual tools.

### Supported Data Types

TOON serialization supports:

- Dictionaries (objects)
- Lists (arrays)
- Strings
- Numbers (int, float)
- Booleans
- Null values
- Nested combinations of the above

### Error Handling

If serialization fails for any reason:

- An error is logged
- The original response is returned unchanged
- The client receives valid data in the fallback format

## Performance Considerations

### Token Savings

Token reduction varies by data structure:

- **Flat Objects**: 20-30% reduction
- **Nested Objects**: 30-45% reduction
- **Uniform Arrays**: 40-60% reduction
- **Mixed Content**: 25-40% reduction

### Processing Overhead

TOON serialization adds minimal overhead:

- Serialization time: <5ms for typical responses
- Memory usage: Similar to JSON serialization
- CPU impact: Negligible for most workloads

### Best Practices

1. **Enable for Production**: TOON is production-ready and stable
2. **Use with AI Agents**: Maximize token efficiency for LLM interactions
3. **Monitor Token Usage**: Track actual savings in your use case
4. **Test Compatibility**: Verify client tools handle TOON format
5. **Document for Users**: Inform users of the format being used

## Troubleshooting

### Common Issues

**Issue: Client doesn't recognize TOON format**
- Solution: Ensure client supports text/plain responses or switch to JSON

**Issue: Data appears malformed**
- Solution: Verify the data structure is compatible with TOON serialization

**Issue: Want to disable for specific tools**
- Solution: TOON is applied globally; switch server config to JSON if needed

### Validation

To verify TOON is enabled:

1. Start the server with TOON configuration
2. Call any tool that returns structured data
3. Check the response format in the client

## Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [TOON Python Library](https://github.com/toon-format/toon-python)
- [TOON Format Specification](https://github.com/toon-format)
- [Itential Platform API Reference](https://docs.itential.com)
- [MCP Protocol Specification](https://modelcontextprotocol.io)

## Support

For issues or questions about TOON format:

1. Check the server logs for serialization errors
2. Verify configuration settings
3. Test with JSON format to isolate the issue
4. Report bugs to the Itential MCP project repository
