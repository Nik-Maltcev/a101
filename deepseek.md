### Invoke Chat API via Python (OpenAI SDK)

Source: https://api-docs.deepseek.com/index

This Python example shows how to use the OpenAI SDK to interact with the DeepSeek API. Ensure you have the SDK installed (`pip3 install openai`). You need to configure the `OpenAI` client with your API key and the DeepSeek base URL. The code sends a chat completion request and prints the response content.

```python
# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)

```

--------------------------------

### Invoke Chat API via Node.js (OpenAI SDK)

Source: https://api-docs.deepseek.com/index

This Node.js example demonstrates calling the DeepSeek chat API using the OpenAI SDK. First, install the SDK (`npm install openai`). Configure the `OpenAI` client with your API key and the DeepSeek base URL. The `main` function makes a chat completion request and logs the content of the assistant's reply.

```javascript
// Please install OpenAI SDK first: `npm install openai`

import OpenAI from "openai";

const openai = new OpenAI({
        baseURL: 'https://api.deepseek.com',
        apiKey: process.env.DEEPSEEK_API_KEY,
});

async function main() {
  const completion = await openai.chat.completions.create({
    messages: [{ role: "system", content: "You are a helpful assistant." }],
    model: "deepseek-chat",
  });

  console.log(completion.choices[0].message.content);
}

main();

```

--------------------------------

### Python Tool Calls Example: Get Weather

Source: https://api-docs.deepseek.com/guides/tool_calls

Demonstrates how to use the Deepseek API with Python to enable tool calls for retrieving weather information. It shows the setup of the OpenAI client, defining tool functions, and managing the message flow for a user query. The model suggests a tool call, which is then simulated with a response.

```python
from openai import OpenAI

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

messages = [{"role": "user", "content": "How's the weather in Hangzhou, Zhejiang?"}]
message = send_messages(messages)
print(f"User>\t {messages[0]['content']}")

tool = message.tool_calls[0]
messages.append(message)

messages.append({"role": "tool", "tool_call_id": tool.id, "content": "24℃"})
message = send_messages(messages)
print(f"Model>\t {message.content}")

```

--------------------------------

### List Models - Go Request

Source: https://api-docs.deepseek.com/api/list-models

Demonstrates how to list Deepseek API models using Go. This example shows how to create an HTTP GET request, set the required headers (Authorization and Accept), send the request, and process the JSON response.

```go
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
)

func main() {
	url := "https://api.deepseek.com/models"

	client := &http.Client{}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		fmt.Println("Error creating request:", err)
		return
	}

	req.Header.Set("Authorization", "Bearer <TOKEN>")
	req.Header.Set("Accept", "application/json")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending request:", err)
		return
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response body:", err)
		return
	}

	fmt.Println(string(body))
}
```

--------------------------------

### Access V3.1-Terminus API with Python SDK

Source: https://api-docs.deepseek.com/guides/comparison_testing

This Python code example shows how to use the OpenAI SDK to interact with the DeepSeek V3.1-Terminus API. Users need to install the SDK and configure the OpenAI client with the specific base URL for V3.1-Terminus and their API key. The output verifies the model name used for the response.

```python
# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com/v3.1_terminus_expires_on_20251015")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(f"Model is: {response.model}")
print(f"Output is: {response.choices[0].message.content}")

```

--------------------------------

### Access V3.1-Terminus API with Node.js SDK

Source: https://api-docs.deepseek.com/guides/comparison_testing

This Node.js example utilizes the OpenAI SDK to connect to the DeepSeek V3.1-Terminus API. It requires installing the SDK and setting the `baseURL` and `apiKey` for the OpenAI client. The script then makes a chat completion request and logs the model name and content from the response.

```javascript
// Please install OpenAI SDK first: `npm install openai`

import OpenAI from "openai";

const openai = new OpenAI({
        baseURL: 'https://api.deepseek.com/v3.1_terminus_expires_on_20251015',
        apiKey: process.env.DEEPSEEK_API_KEY,
});

async function main() {
  const completion = await openai.chat.completions.create({
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: "Hello!."}
    ],
    model: "deepseek-chat",
  });

  console.log("Model is:", completion.model)
  console.log("Output is:", completion.choices[0].message.content);
}

main();

```

--------------------------------

### Install Anthropic SDK for Python

Source: https://api-docs.deepseek.com/guides/anthropic_api

This command installs the official Anthropic SDK for Python, which is required to interact with the Anthropic API, including DeepSeek models. Ensure you have Python and pip installed.

```bash
pip install anthropic
```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using Go. This code snippet demonstrates how to construct the JSON payload and send a POST request.

```go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
)

func main() {
	url := "https://api.deepseek.com/beta"

	requestBody := map[string]interface{}{
		"model": "deepseek-chat",
		"prompt": "Once upon a time, ",
		"echo": false,
		"frequency_penalty": 0,
		"logprobs": 0,
		"max_tokens": 1024,
		"presence_penalty": 0,
		"stop": nil,
		"stream": false,
		"stream_options": nil,
		"suffix": nil,
		"temperature": 1,
		"top_p": 1
	}

	payload, err := json.Marshal(requestBody)
	if err != nil {
		fmt.Println("Error marshaling JSON:", err)
		return
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(payload))
	if err != nil {
		fmt.Println("Error creating request:", err)
		return
	}

	req.Header.Set("Authorization", "Bearer YOUR_API_KEY")
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending request:", err)
		return
	}

	defer resp.Body.Close()

	var result map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		fmt.Println("Error decoding response:", err)
		return
	}

	fmt.Println(result)
}

```

--------------------------------

### Get User Balance - Example JSON Response

Source: https://api-docs.deepseek.com/api/get-user-balance

This is an example JSON response from the Deepseek API when requesting user balance. It shows the structure, including whether the balance is sufficient for API calls and details about the balance in different currencies.

```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "110.00",
      "granted_balance": "10.00",
      "topped_up_balance": "100.00"
    }
  ]
}
```

--------------------------------

### Example Chat Completion Response (JSON)

Source: https://api-docs.deepseek.com/api/create-chat-completion

An example of a chat completion response from the Deepseek API, illustrating a simple assistant message. This example shows a typical structure for a successful completion.

```json
{
  "id": "930c60df-bf64-41c9-a88e-3ec75f81e00e",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "Hello! How can I help you today?",
        "role": "assistant"
      }
    }
  ],
  "created": 1705651092,
  "model": "deepseek-chat",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 10,
    "prompt_tokens": 16,
    "total_tokens": 26
  }
}
```

--------------------------------

### Python Conversation History Example (Round 1)

Source: https://api-docs.deepseek.com/guides/multi_round_chat

Illustrates the 'messages' list structure for the first turn of a conversation with the DeepSeek API. This list contains only the initial user query, as no prior history exists.

```python
[
    {"role": "user", "content": "What's the highest mountain in the world?"}
]
```

--------------------------------

### Initiate a Conversation Turn (Python)

Source: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode

Demonstrates how to initiate a conversational turn by setting up the initial messages list with a user query and calling the `run_turn` function. This example shows a single turn interaction.

```python
# The user starts a question
turn = 1
messages = [{
    "role": "user",
    "content": "How's the weather in Hangzhou Tomorrow"
}]
run_turn(turn, messages)
```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using PowerShell. This script demonstrates how to use 'Invoke-RestMethod' to send the POST request with the JSON payload.

```powershell
$url = "https://api.deepseek.com/beta"
$apiKey = "YOUR_API_KEY"

$requestBody = @{
  model = "deepseek-chat"
  prompt = "Once upon a time, "
  echo = $false
  frequency_penalty = 0
  logprobs = 0
  max_tokens = 1024
  presence_penalty = 0
  stop = $null
  stream = $false
  stream_options = $null
  suffix = $null
  temperature = 1
  top_p = 1
}

$headers = @{
  "Authorization" = "Bearer $apiKey"
  "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body ($requestBody | ConvertTo-Json -Depth 10)

```

--------------------------------

### Execute Claude Code in Project Directory

Source: https://api-docs.deepseek.com/guides/anthropic_api

After installing and configuring Claude Code, navigate to your project directory and execute the 'claude' command to start using it. This assumes the environment variables are set correctly in your current shell session.

```bash
cd my-project
claude
```

--------------------------------

### List Models - Java Request

Source: https://api-docs.deepseek.com/api/list-models

This Java example shows how to list Deepseek API models. It utilizes the standard Java HTTP client to send a GET request, including the 'Authorization' and 'Accept' headers.

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.io.IOException;

public class DeepseekApiClient {

    public static void main(String[] args) {
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("https://api.deepseek.com/models"))
                .header("Authorization", "Bearer <TOKEN>")
                .header("Accept", "application/json")
                .build();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println(response.body());
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

--------------------------------

### Get User Balance - Node.js Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet provides an example of how to get the user balance from the Deepseek API using Node.js. It demonstrates making an HTTP GET request with headers for authorization and content acceptance.

```javascript
// Example Node.js code would go here, using modules like 'axios' or 'node-fetch'
// to make a GET request to the API endpoint with authentication.
```

--------------------------------

### Python Conversation History Example (Round 2 Input)

Source: https://api-docs.deepseek.com/guides/multi_round_chat

Shows the 'messages' list structure when making the second request to the DeepSeek API. It includes the user's initial query, the assistant's response from the first round, and the new user query.

```python
[
    {"role": "user", "content": "What's the highest mountain in the world?"},
    {"role": "assistant", "content": "The highest mountain in the world is Mount Everest."},
    {"role": "user", "content": "What is the second?"}
]
```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using Python. It shows how to structure the request payload and send it using the 'requests' library.

```python
import requests

url = "https://api.deepseek.com/beta"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
payload = {
    "model": "deepseek-chat",
    "prompt": "Once upon a time, ",
    "echo": False,
    "frequency_penalty": 0,
    "logprobs": 0,
    "max_tokens": 1024,
    "presence_penalty": 0,
    "stop": None,
    "stream": False,
    "stream_options": None,
    "suffix": None,
    "temperature": 1,
    "top_p": 1
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())

```

--------------------------------

### Enable JSON Output with DeepSeek API (Python)

Source: https://api-docs.deepseek.com/guides/json_mode

This code demonstrates how to configure the DeepSeek API client in Python to ensure the model returns output in a valid JSON object format. It requires setting the 'response_format' parameter and includes a system prompt with a JSON example to guide the model. The output is then parsed using the `json` library.

```python
import json
from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

system_prompt = """
The user will provide some exam text. Please parse the "question" and "answer" and output them in JSON format.   

EXAMPLE INPUT:   
Which is the highest mountain in the world? Mount Everest.  

EXAMPLE JSON OUTPUT:  
{
    "question": "Which is the highest mountain in the world?",
    "answer": "Mount Everest"
}
"""

user_prompt = "Which is the longest river in the world? The Nile River."

messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    response_format={
        'type': 'json_object'
    }
)

print(json.loads(response.choices[0].message.content))
```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using C#. This code snippet demonstrates how to use 'HttpClient' to send the POST request with the JSON payload.

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

public class DeepseekApiClient
{
    private static readonly HttpClient client = new HttpClient();

    public static async Task MakeRequestAsync()
    {
        var url = "https://api.deepseek.com/beta";
        var apiKey = "YOUR_API_KEY";

        var requestBody = new {
            model = "deepseek-chat",
            prompt = "Once upon a time, ",
            echo = false,
            frequency_penalty = 0,
            logprobs = 0,
            max_tokens = 1024,
            presence_penalty = 0,
            stop = (object)null,
            stream = false,
            stream_options = (object)null,
            suffix = (object)null,
            temperature = 1,
            top_p = 1
        };

        var jsonPayload = System.Text.Json.JsonSerializer.Serialize(requestBody);
        var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

        client.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", apiKey);

        try
        {
            HttpResponseMessage response = await client.PostAsync(url, content);
            response.EnsureSuccessStatusCode(); // Throws an exception if the status code is not 2xx
            string responseBody = await response.Content.ReadAsStringAsync();
            Console.WriteLine(responseBody);
        }
        catch (HttpRequestException e)
        {
            Console.WriteLine($"Request error: {e.Message}");
        }
    }

    public static async Task Main(string[] args)
    {
        await MakeRequestAsync();
    }
}

```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

An example of a cURL request to the Deepseek API for text completion. This demonstrates the necessary parameters such as model, prompt, and various generation controls like temperature and max_tokens.

```curl
curl -X POST https://api.deepseek.com/beta \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{ 
  "model": "deepseek-chat",
  "prompt": "Once upon a time, ",
  "echo": false,
  "frequency_penalty": 0,
  "logprobs": 0,
  "max_tokens": 1024,
  "presence_penalty": 0,
  "stop": null,
  "stream": false,
  "stream_options": null,
  "suffix": null,
  "temperature": 1,
  "top_p": 1
}'
```

--------------------------------

### Python FIM Completion Example

Source: https://api-docs.deepseek.com/guides/fim_completion

Demonstrates how to use the Deepseek API for FIM (Fill In the Middle) completion using Python. This snippet shows setting up the OpenAI client with a specific API key and base URL for beta features, and then making a completion request with a model, prompt, suffix, and max tokens. The output is the generated text, typically code.

```python
from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com/beta",
)

response = client.completions.create(
    model="deepseek-chat",
    prompt="def fib(a):",
    suffix="    return fib(a-1) + fib(a-2)",
    max_tokens=128
)
print(response.choices[0].text)
```

--------------------------------

### List Models - PowerShell Request

Source: https://api-docs.deepseek.com/api/list-models

A PowerShell script to list Deepseek API models. This example uses 'Invoke-RestMethod' to send a GET request, including the necessary 'Authorization' and 'Accept' headers.

```powershell
$url = "https://api.deepseek.com/models"
$token = "<TOKEN>"

$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/json"
}

Invoke-RestMethod -Uri $url -Method Get -Headers $headers
```

--------------------------------

### Python Chat Prefix Completion Example

Source: https://api-docs.deepseek.com/guides/chat_prefix_completion

Demonstrates how to perform chat prefix completion using Python with the Deepseek API. It shows setting the assistant's prefix message and stopping the generation at specific tokens. Requires the `openai` library and the Deepseek beta endpoint.

```python
from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com/beta",
)

messages = [
    {"role": "user", "content": "Please write quick sort code"},
    {"role": "assistant", "content": "```python\n", "prefix": True}
]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    stop=["```"],
)
print(response.choices[0].message.content)

```

--------------------------------

### Install and Configure Claude Code with DeepSeek

Source: https://api-docs.deepseek.com/guides/anthropic_api

This snippet shows how to install the Claude Code package globally and configure environment variables to use DeepSeek models. It includes setting the Anthropic base URL, authentication token, API timeout, and default models. Ensure you replace `${YOUR_API_KEY}` with your actual DeepSeek API key.

```bash
npm install -g @anthropic-ai/claude-code

export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=${YOUR_API_KEY}
export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

--------------------------------

### Tool Calls - Non-thinking Mode Example

Source: https://api-docs.deepseek.com/guides/tool_calls

Demonstrates how to use Tool Calls for external tool integration in non-thinking mode, using Python and the OpenAI client library. This example shows fetching weather information.

```APIDOC
## POST /chat/completions (Conceptual)

### Description
This endpoint is used to interact with the DeepSeek chat model, enabling it to call external tools based on user requests. The example provided shows a Python implementation for fetching weather information.

### Method
POST

### Endpoint
https://api.deepseek.com/chat/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for chat completion (e.g., "deepseek-chat").
- **messages** (array) - Required - An array of message objects representing the conversation history.
  - **role** (string) - Required - The role of the message author ("user", "assistant", "tool").
  - **content** (string) - Required - The content of the message.
  - **tool_call_id** (string) - Required (if role is "tool") - The ID of the tool call being responded to.
- **tools** (array) - Optional - A list of tool definitions the model can use.
  - **type** (string) - Required - The type of the tool (e.g., "function").
  - **function** (object) - Required - The function definition.
    - **name** (string) - Required - The name of the function.
    - **description** (string) - Optional - A description of what the function does.
    - **parameters** (object) - Required - The JSON schema describing the function's parameters.
      - **type** (string) - Required - The type of the parameter (e.g., "object").
      - **properties** (object) - Optional - An object defining the properties of the parameter.
      - **required** (array) - Optional - An array of strings listing the required parameters.

### Request Example
```python
from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
]

messages = [{"role": "user", "content": "How's the weather in Hangzhou, Zhejiang?"}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools
)

# Process the response to extract tool calls or content
```

### Response
#### Success Response (200)
- **choices** (array) - An array of chat completion choices.
  - **message** (object) - The message content from the model.
    - **role** (string) - The role of the message author ("assistant").
    - **content** (string) - The content of the message. If a tool is called, this might be null or contain tool call information.
    - **tool_calls** (array) - An array of tool calls generated by the model.
      - **id** (string) - The ID of the tool call.
      - **type** (string) - The type of the tool call (e.g., "function").
      - **function** (object) - Information about the function to call.
        - **name** (string) - The name of the function to call.
        - **arguments** (string) - A JSON string representing the arguments for the function call.

#### Response Example (Tool Call)
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "get_weather",
              "arguments": "{\"location\": \"Hangzhou\"}"
            }
          }
        ]
      }
    }
  ]
}
```

#### Response Example (Natural Language)
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "The current temperature in Hangzhou is 24°C."
      }
    }
  ]
}
```
```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using Ruby. This code snippet demonstrates how to use the 'net/http' library to send the POST request with the JSON payload.

```ruby
require 'net/http'
require 'uri'
require 'json'

url = URI.parse('https://api.deepseek.com/beta')
api_key = 'YOUR_API_KEY'

request_body = {
  "model": "deepseek-chat",
  "prompt": "Once upon a time, ",
  "echo": false,
  "frequency_penalty": 0,
  "logprobs": 0,
  "max_tokens": 1024,
  "presence_penalty": 0,
  "stop": nil,
  "stream": false,
  "stream_options": nil,
  "suffix": nil,
  "temperature": 1,
  "top_p": 1
}

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["Authorization"] = "Bearer #{api_key}"
request["Content-Type"] = "application/json"
request.body = request_body.to_json

response = http.request(request)
puts JSON.parse(response.body)

```

--------------------------------

### List Models - Ruby Request

Source: https://api-docs.deepseek.com/api/list-models

A Ruby example for retrieving the list of Deepseek API models. This code uses the 'net/http' library to perform an HTTP GET request, including the necessary authentication and content-type headers.

```ruby
require 'net/http'
require 'uri'

uri = URI.parse("https://api.deepseek.com/models")

request = Net::HTTP::Get.new(uri)
request["Authorization"] = "Bearer <TOKEN>"
request["Accept"] = "application/json"

response = Net::HTTP.start(uri.hostname, uri.port, :use_ssl => uri.scheme == "https") do |http|
  http.request(request)
end

puts response.body
```

--------------------------------

### AnyOf for Multiple Valid Formats

Source: https://api-docs.deepseek.com/guides/tool_calls

Allows a field to match any one of the provided schemas, enabling flexibility. This example shows an 'account' field that can be either an email address or a 11-digit phone number.

```json
{
    "type": "object",
    "properties": {
    "account": {
        "anyOf": [
            { "type": "string", "format": "email", "description": "可以是电子邮件地址" },
            { "type": "string", "pattern": "^\\d{11}$", "description": "或11位手机号码" }
        ]
    }
  }
}
```

--------------------------------

### List Models - PHP Request

Source: https://api-docs.deepseek.com/api/list-models

A PHP example for fetching the list of Deepseek API models. This code uses cURL to make the HTTP GET request, ensuring the 'Authorization' and 'Accept' headers are included.

```php
<?php

$url = 'https://api.deepseek.com/models';
$token = '<TOKEN>'; // Replace with your actual token

$ch = curl_init($url);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    'Authorization: Bearer ' . $token,
    'Accept: application/json'
));

$response = curl_exec($ch);

if (curl_errno($ch)) {
    echo 'Error:' . curl_error($ch);
} else {
    echo $response;
}

curl_close($ch);
?>
```

--------------------------------

### Example 3: Few-shot Learning Cache Hit

Source: https://api-docs.deepseek.com/guides/kv_cache

Shows how context caching benefits few-shot learning by reusing the prompt examples provided in the initial request when subsequent requests have similar prefixes.

```APIDOC
## Example 3: Using Few-shot Learning

### Description
Few-shot learning involves providing example interactions within the prompt to guide the model's output. Context caching significantly reduces the cost associated with few-shot learning because the common prefix, consisting of the provided examples, can be cached and reused.

### First Request (with 4-shot examples)
```json
{
  "messages": [
    {"role": "system", "content": "You are a history expert. The user will provide a series of questions, and your answers should be concise and start with `Answer:`"},
    {"role": "user", "content": "In what year did Qin Shi Huang unify the six states?"},
    {"role": "assistant", "content": "Answer: 221 BC"},
    {"role": "user", "content": "Who was the founder of the Han Dynasty?"},
    {"role": "assistant", "content": "Answer: Liu Bang"},
    {"role": "user", "content": "Who was the last emperor of the Tang Dynasty?"},
    {"role": "assistant", "content": "Answer: Li Zhu"},
    {"role": "user", "content": "Who was the founding emperor of the Ming Dynasty?"},
    {"role": "assistant", "content": "Answer: Zhu Yuanzhang"},
    {"role": "user", "content": "Who was the founding emperor of the Qing Dynasty?"}
  ]
}
```

### Second Request (with modified last question)
```json
{
  "messages": [
    {"role": "system", "content": "You are a history expert. The user will provide a series of questions, and your answers should be concise and start with `Answer:`"},
    {"role": "user", "content": "In what year did Qin Shi Huang unify the six states?"},
    {"role": "assistant", "content": "Answer: 221 BC"},
    {"role": "user", "content": "Who was the founder of the Han Dynasty?"},
    {"role": "assistant", "content": "Answer: Liu Bang"},
    {"role": "user", "content": "Who was the last emperor of the Tang Dynasty?"},
    {"role": "assistant", "content": "Answer: Li Zhu"},
    {"role": "user", "content": "Who was the founding emperor of the Ming Dynasty?"},
    {"role": "assistant", "content": "Answer: Zhu Yuanzhang"},
    {"role": "user", "content": "When did the Shang Dynasty fall?"}
  ]
}
```

### Cache Hit Explanation
In this 4-shot example, the second request differs from the first only in the final user question. The preceding four rounds of dialogue (system message and alternating user/assistant messages) form a significant prefix that can be reused, resulting in a 'cache hit' and reduced processing cost.
```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using Node.js. This code snippet shows how to use the 'axios' library to send the POST request with the appropriate JSON payload.

```javascript
const axios = require('axios');

const url = 'https://api.deepseek.com/beta';
const apiKey = 'YOUR_API_KEY';

const requestData = {
  model: 'deepseek-chat',
  prompt: 'Once upon a time, ',
  echo: false,
  frequency_penalty: 0,
  logprobs: 0,
  max_tokens: 1024,
  presence_penalty: 0,
  stop: null,
  stream: false,
  stream_options: null,
  suffix: null,
  temperature: 1,
  top_p: 1
};

axios.post(url, requestData, {
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.error('Error making API request:', error);
  });

```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using Java. This code snippet demonstrates how to use 'HttpURLConnection' to send the POST request with the JSON payload.

```java
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;

public class DeepseekApiClient {

    public static void main(String[] args) {
        try {
            URL url = new URL("https://api.deepseek.com/beta");
            String apiKey = "YOUR_API_KEY";

            String requestBody = "{\"model\":\"deepseek-chat\",\"prompt\":\"Once upon a time, \",\"echo\":false,\"frequency_penalty\":0,\"logprobs\":0,\"max_tokens\":1024,\"presence_penalty\":0,\"stop\":null,\"stream\":false,\"stream_options\":null,\"suffix\":null,\"temperature\":1,\"top_p\":1}";

            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Authorization", "Bearer " + apiKey);
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = requestBody.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            int responseCode = connection.getResponseCode();
            System.out.println("Response Code: " + responseCode);

            try (Scanner scanner = new Scanner(connection.getInputStream(), StandardCharsets.UTF_8.name())) {
                while (scanner.hasNextLine()) {
                    System.out.println(scanner.nextLine());
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

```

--------------------------------

### List Models - Python Request

Source: https://api-docs.deepseek.com/api/list-models

Provides a Python example for listing Deepseek API models. This code snippet utilizes the 'requests' library to make a GET request to the API endpoint, including necessary headers for authentication and content type.

```python
import requests

url = "https://api.deepseek.com/models"
headers = {
    "Authorization": "Bearer <TOKEN>",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

--------------------------------

### Get User Balance - Go Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet illustrates how to fetch user balance data from the Deepseek API using Go. It involves making an HTTP GET request and handling the JSON response, including setting necessary headers for authentication.

```go
// Example Go code would go here, using the 'net/http' package to make
// a GET request to the API endpoint with authentication headers.
```

--------------------------------

### Deepseek API Text Completion Request Example

Source: https://api-docs.deepseek.com/api/create-completion

Example of making a text completion request to the Deepseek API using PHP. This code snippet demonstrates how to use cURL functions to send the POST request with the JSON payload.

```php
<?php

$url = 'https://api.deepseek.com/beta';
$apiKey = 'YOUR_API_KEY';

$requestData = [
    'model' => 'deepseek-chat',
    'prompt' => 'Once upon a time, ',
    'echo' => false,
    'frequency_penalty' => 0,
    'logprobs' => 0,
    'max_tokens' => 1024,
    'presence_penalty' => 0,
    'stop' => null,
    'stream' => false,
    'stream_options' => null,
    'suffix' => null,
    'temperature' => 1,
    'top_p' => 1
];

$jsonData = json_encode($requestData);

$ch = curl_init($url);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $apiKey,
    'Content-Type: application/json'
]);

$response = curl_exec($ch);

if (curl_errno($ch)) {
    echo 'Curl error: ' . curl_error($ch);
} else {
    echo $response;
}

curl_close($ch);

?>

```

--------------------------------

### Few-shot Learning Example for Context Caching

Source: https://api-docs.deepseek.com/guides/kv_cache

Shows how context caching significantly reduces costs in few-shot learning scenarios. The second request reuses the majority of the prompt from the first request (4 shots), except for the last user query, leading to a substantial cache hit.

```json
messages: [
    {"role": "system", "content": "You are a history expert. The user will provide a series of questions, and your answers should be concise and start with `Answer:`"},
    {"role": "user", "content": "In what year did Qin Shi Huang unify the six states?"},
    {"role": "assistant", "content": "Answer: 221 BC"},
    {"role": "user", "content": "Who was the founder of the Han Dynasty?"},
    {"role": "assistant", "content": "Answer: Liu Bang"},
    {"role": "user", "content": "Who was the last emperor of the Tang Dynasty?"},
    {"role": "assistant", "content": "Answer: Li Zhu"},
    {"role": "user", "content": "Who was the founding emperor of the Ming Dynasty?"},
    {"role": "assistant", "content": "Answer: Zhu Yuanzhang"},
    {"role": "user", "content": "Who was the founding emperor of the Qing Dynasty?"}
]

```

```json
messages: [
    {"role": "system", "content": "You are a history expert. The user will provide a series of questions, and your answers should be concise and start with `Answer:`"},
    {"role": "user", "content": "In what year did Qin Shi Huang unify the six states?"},
    {"role": "assistant", "content": "Answer: 221 BC"},
    {"role": "user", "content": "Who was the founder of the Han Dynasty?"},
    {"role": "assistant", "content": "Answer: Liu Bang"},
    {"role": "user", "content": "Who was the last emperor of the Tang Dynasty?"},
    {"role": "assistant", "content": "Answer: Li Zhu"},
    {"role": "user", "content": "Who was the founding emperor of the Ming Dynasty?"},
    {"role": "assistant", "content": "Answer: Zhu Yuanzhang"},
    {"role": "user", "content": "When did the Shang Dynasty fall?"}

]

```

--------------------------------

### Completions API (FIM)

Source: https://api-docs.deepseek.com/news/news0725

The new Completions API supports FIM (Fill-In-the-Middle) completion, allowing for custom prefixes and suffixes to guide content generation. This is useful for tasks like code completion and story continuation. Beta features require setting the base URL to `https://api.deepseek.com/beta`.

```APIDOC
## POST /completions

### Description
This endpoint supports Fill-In-the-Middle (FIM) completion, enabling users to provide optional prefixes and suffixes to guide the model in completing content. This is particularly useful for code generation and text completion tasks. Beta features are enabled by setting the `base_url` to `https://api.deepseek.com/beta`.

### Method
POST

### Endpoint
/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for completion (e.g., `deepseek-coder`).
- **prompt** (string) - Required - The text prompt, potentially including prefix and suffix for FIM.
- **suffix** (string) - Optional - The suffix for FIM completion.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate.
- **temperature** (number) - Optional - Controls randomness.
- **stop** (string or array) - Optional - Sequences where the API will stop generating further tokens.

### Request Example
```json
{
  "model": "deepseek-coder",
  "prompt": "def fib(n):\n    \"\"\"Return the nth Fibonacci number.\"\"\"\n    ",
  "suffix": "\n    pass",
  "temperature": 0.7
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of the object returned (e.g., `text_completion`).
- **created** (integer) - Unix timestamp of when the response was created.
- **model** (string) - The model used for the response.
- **choices** (array) - An array of completion choices.
  - **index** (integer) - Index of the choice.
  - **text** (string) - The generated completion text.
  - **finish_reason** (string) - The reason the model stopped generating.
- **usage** (object) - Usage statistics for the request.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total tokens used.

#### Response Example
```json
{
  "id": "cmpl-123",
  "object": "text_completion",
  "created": 1677652288,
  "model": "deepseek-coder",
  "choices": [
    {
      "index": 0,
      "text": "\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    else:\n        a, b = 0, 1\n        for _ in range(2, n + 1):\n            a, b = b, a + b\n        return b",
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 60,
    "total_tokens": 75
  }
}
```
```

--------------------------------

### Invoke DeepSeek Model via Anthropic API (Python SDK)

Source: https://api-docs.deepseek.com/guides/anthropic_api

This section details how to install the Anthropic Python SDK, configure the necessary environment variables, and invoke the DeepSeek model using the Anthropic API.

```APIDOC
## Invoke DeepSeek Model via Anthropic API

### Installation

1. Install the Anthropic SDK:

```bash
pip install anthropic
```

### Configuration

2. Set the following environment variables:

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY=${DEEPSEEK_API_KEY}
```

### API Invocation Example (Python)

3. Use the SDK to invoke the API:

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="deepseek-chat",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, how are you?"
                }
            ]
        }
    ]
)
print(message.content)
```

*Note: If an unsupported model name is provided, the API will automatically map it to `deepseek-chat`.*

```

--------------------------------

### Example 1: Long Text Q&A Cache Hit

Source: https://api-docs.deepseek.com/guides/kv_cache

Demonstrates a cache hit scenario with two Q&A requests where the system message and the initial part of the user message (financial report content) are the same.

```APIDOC
## Example 1: Long Text Q&A

### Description
This example illustrates a cache hit in a long text Q&A scenario. The first request asks for a summary, and the second asks for an analysis of the same financial report content. The common prefix, consisting of the system message and the report content in the user message, triggers a cache hit on the second request.

### First Request
```json
{
  "messages": [
    {"role": "system", "content": "You are an experienced financial report analyst..."},
    {"role": "user", "content": "<financial report content>\n\nPlease summarize the key information of this financial report."}
  ]
}
```

### Second Request
```json
{
  "messages": [
    {"role": "system", "content": "You are an experienced financial report analyst..."},
    {"role": "user", "content": "<financial report content>\n\nPlease analyze the profitability of this financial report."}
  ]
}
```

### Cache Hit Explanation
In this example, both requests share the same prefix: the `system` message and the `<financial report content>` part of the `user` message. During the second request, this shared prefix results in a 'cache hit'.
```

--------------------------------

### Get User Balance - Ruby Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet shows how to call the Deepseek API to get the user's balance using Ruby. It includes making a GET request with the required authentication token and specifying the expected response format.

```ruby
# Example Ruby code would go here, using libraries like 'net/http' or 'httparty'
# to make a GET request to the API endpoint with authentication.
```

--------------------------------

### Get User Balance - C# Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet demonstrates how to retrieve user balance information from the Deepseek API using C#. It involves creating an HttpClient, sending a GET request with appropriate headers, and deserializing the JSON response.

```csharp
// Example C# code would go here, using 'HttpClient' to make a GET request
// to the API endpoint with authentication headers.
```

--------------------------------

### $ref and $def for Reusable Schema Definitions

Source: https://api-docs.deepseek.com/guides/tool_calls

Enables modularization by defining reusable schema components using '$def' and referencing them with '$ref'. This example defines an 'author' schema that is then used within an 'authors' array.

```json
{
    "type": "object",
    "properties": {
        "report_date": {
            "type": "string",
            "description": "The date when the report was published"
        },
        "authors": {
            "type": "array",
            "description": "The authors of the report",
            "items": {
                "$ref": "#/$def/author"
            }
        }
    },
    "required": ["report_date", "authors"],
    "additionalProperties": false,
    "$def": {
        "authors": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "author's name"
                },
                "institution": {
                    "type": "string",
                    "description": "author's institution"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "author's email"
                }
            },
            "additionalProperties": false,
            "required": ["name", "institution", "email"]
        }
    }
}
```

--------------------------------

### Get User Balance - PowerShell Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet demonstrates how to get the user balance from the Deepseek API using PowerShell. It utilizes the 'Invoke-RestMethod' cmdlet to send a GET request with the required authentication token and headers.

```powershell
# Example PowerShell code would go here, using Invoke-RestMethod to make a
# GET request to the API endpoint with authentication headers.
```

--------------------------------

### GET /user/balance

Source: https://api-docs.deepseek.com/api/get-user-balance

Retrieves the current balance information for the authenticated user.

```APIDOC
## GET /user/balance

### Description
Retrieves the current balance information for the authenticated user.

### Method
GET

### Endpoint
https://api.deepseek.com/user/balance

### Parameters
#### Query Parameters
None

#### Request Body
None

### Request Example
```curl
curl -L -X GET 'https://api.deepseek.com/user/balance' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer <TOKEN>'
```

### Response
#### Success Response (200)
- **is_available** (boolean) - Whether the user's balance is sufficient for API calls.
- **balance_infos** (object[]) - An array of balance information objects.
  - **currency** (string) - The currency of the balance. Possible values: [`CNY`, `USD`].
  - **total_balance** (string) - The total available balance, including granted and topped-up balance.
  - **granted_balance** (string) - The total not expired granted balance.
  - **topped_up_balance** (string) - The total topped-up balance.

#### Response Example
```json
{
  "is_available": true,
  "balance_infos": [
    {
      "currency": "CNY",
      "total_balance": "110.00",
      "granted_balance": "10.00",
      "topped_up_balance": "100.00"
    }
  ]
}
```
```

--------------------------------

### GET /models

Source: https://api-docs.deepseek.com/api/list-models

Lists the currently available models and provides basic information about each one, such as the owner and availability.

```APIDOC
## GET /models

### Description
Lists the currently available models and provides basic information about each one such as the owner and availability. Check Models & Pricing for our currently supported models.

### Method
GET

### Endpoint
https://api.deepseek.com/models

### Parameters

#### Query Parameters
None

#### Request Body
None

### Request Example
```json
{
  "example": ""
}
```

### Response
#### Success Response (200)
- **object** (string) - The object type, always "list".
- **data** (array) - An array of model objects.
  - **id** (string) - The model identifier.
  - **object** (string) - The object type, always "model".
  - **owned_by** (string) - The organization that owns the model.

#### Response Example
```json
{
  "object": "list",
  "data": [
    {
      "id": "deepseek-chat",
      "object": "model",
      "owned_by": "deepseek"
    },
    {
      "id": "deepseek-reasoner",
      "object": "model",
      "owned_by": "deepseek"
    }
  ]
}
```

### Authentication
Bearer Token
```

--------------------------------

### Get User Balance - PHP Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet shows how to fetch user balance details from the Deepseek API using PHP. It includes making a GET request with cURL or a similar HTTP client, setting the necessary authorization headers, and parsing the JSON response.

```php
// Example PHP code would go here, using cURL or 'file_get_contents' with context
// to make a GET request to the API endpoint with authentication.
```

--------------------------------

### Get User Balance - Python Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet shows how to retrieve user balance information from the Deepseek API using Python. It utilizes the 'requests' library to make a GET request with appropriate headers for authentication and content type.

```python
# Example Python code would go here, making a GET request to the API endpoint
# using libraries like 'requests'.
```

--------------------------------

### Get User Balance - Java Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet illustrates how to obtain user balance data from the Deepseek API using Java. It involves using Java's HTTP client (e.g., Apache HttpClient, OkHttp, or built-in HttpURLConnection) to send a GET request with authentication.

```java
// Example Java code would go here, using HttpURLConnection or a library like
// Apache HttpClient to make a GET request to the API endpoint with authentication.
```

--------------------------------

### Get User Balance - CURL Request

Source: https://api-docs.deepseek.com/api/get-user-balance

This snippet demonstrates how to make a GET request to the Deepseek API's user balance endpoint using cURL. It includes the necessary URL, headers for accepting JSON and authentication with a Bearer token.

```curl
curl -L -X GET 'https://api.deepseek.com/user/balance' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer <TOKEN>'
```

--------------------------------

### Use DeepSeek in Claude Code

Source: https://api-docs.deepseek.com/guides/anthropic_api

This section provides instructions on installing Claude Code and configuring environment variables to use DeepSeek models within the Claude Code environment.

```APIDOC
## Use DeepSeek in Claude Code

### Installation

1. Install Claude Code globally:

```bash
npm install -g @anthropic-ai/claude-code
```

### Configuration

2. Set the following environment variables:

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=${YOUR_API_KEY}
export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export ANTHROPIC_SMALL_FAST_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

*Note: `API_TIMEOUT_MS` is set to 10 minutes (600000 ms) to prevent timeouts with long outputs.*

### Execution

3. Navigate to your project directory and execute Claude Code:

```bash
cd my-project
claude
```
```

--------------------------------

### Multi-round Conversation Example for Context Caching

Source: https://api-docs.deepseek.com/guides/kv_cache

Illustrates context caching in multi-round conversations. The second request reuses the system message and the initial user message from the first request, resulting in a cache hit for the repeated prefix.

```json
messages: [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is the capital of China?"}
]

```

```json
messages: [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is the capital of China?"},
    {"role": "assistant", "content": "The capital of China is Beijing."},
    {"role": "user", "content": "What is the capital of the United States?"}
]

```

--------------------------------

### Long Text Q&A Example for Context Caching

Source: https://api-docs.deepseek.com/guides/kv_cache

Demonstrates how context caching applies to long text question-answering scenarios. The overlapping 'system' message and the initial part of the 'user' message in the second request can be cached, leading to a cache hit.

```json
messages: [
    {"role": "system", "content": "You are an experienced financial report analyst..."}
    {"role": "user", "content": "<financial report content>\n\nPlease summarize the key information of this financial report."} 
]

```

```json
messages: [
    {"role": "system", "content": "You are an experienced financial report analyst..."}
    {"role": "user", "content": "<financial report content>\n\nPlease analyze the profitability of this financial report."} 
]

```

--------------------------------

### JSON Schema Object Definition Example

Source: https://api-docs.deepseek.com/guides/tool_calls

Provides an example of defining an 'object' type within a JSON schema for use in strict mode tool definitions. This highlights the requirement for all object properties to be explicitly listed in 'required' and the necessity of setting 'additionalProperties' to 'false'.

```json
{
    "type": "object",
    "properties": {
        "name": { "type": "string" },
        "age": { "type": "integer" }
    },
    "required": ["name", "age"],
    "additionalProperties": false
}

```

--------------------------------

### Array Structure Definition

Source: https://api-docs.deepseek.com/guides/tool_calls

Defines an array where each item must conform to a specific schema. This example specifies an array of strings, each representing a keyword. Unsupported parameters include minItems and maxItems.

```json
{
    "type": "object",
    "properties": {
        "keywords": {
            "type": "array",
            "description": "Five keywords of the article, sorted by importance",
            "items": {
                "type": "string",
                "description": "A concise and accurate keyword or phrase."
            }
        }
    },
    "required": ["keywords"],
    "additionalProperties": false
}
```

--------------------------------

### Python Multi-round Conversation with DeepSeek API

Source: https://api-docs.deepseek.com/guides/multi_round_chat

Demonstrates how to maintain conversation history for multi-turn interactions using the DeepSeek /chat/completions API in Python. It initializes the OpenAI client with DeepSeek's base URL and API key, then iteratively sends user messages along with the accumulated conversation history. The response from the model is appended to the history for subsequent turns. Dependencies include the 'openai' library.

```python
from openai import OpenAI
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# Round 1
messages = [{"role": "user", "content": "What's the highest mountain in the world?"}]
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

messages.append(response.choices[0].message)
print(f"Messages Round 1: {messages}")

# Round 2
messages.append({"role": "user", "content": "What is the second?"})
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
)

messages.append(response.choices[0].message)
print(f"Messages Round 2: {messages}")
```

--------------------------------

### Example 2: Multi-round Conversation Cache Hit

Source: https://api-docs.deepseek.com/guides/kv_cache

Illustrates a cache hit in a multi-round conversation. The second request includes the entire first request's context plus a new user query, allowing the initial parts to be cached.

```APIDOC
## Example 2: Multi-round Conversation

### Description
This example demonstrates how context caching applies to multi-round conversations. The second request builds upon the first by adding an assistant response and a new user question. The initial system and user messages from the first request are reused, resulting in a cache hit.

### First Request
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is the capital of China?"}
  ]
}
```

### Second Request
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is the capital of China?"},
    {"role": "assistant", "content": "The capital of China is Beijing."},
    {"role": "user", "content": "What is the capital of the United States?"}
  ]
}
```

### Cache Hit Explanation
In this scenario, the second request reuses the `system` message and the first `user` message from the first request. This reuse of the initial context triggers a 'cache hit'.
```

--------------------------------

### Non-Streaming API Call with Thinking Mode (Python)

Source: https://api-docs.deepseek.com/guides/thinking_mode

Provides a Python example for making a non-streaming API call to the DeepSeek model with thinking mode enabled. It shows how to handle the `reasoning_content` and the final `content` from the response for both the first and subsequent turns of a conversation.

```python
from openai import OpenAI
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# Turn 1
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages
)

reasoning_content = response.choices[0].message.reasoning_content
content = response.choices[0].message.content

# Turn 2
messages.append({'role': 'assistant', 'content': content})
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages
)
# ...

```

--------------------------------

### List Models - JSON Response Schema and Example

Source: https://api-docs.deepseek.com/api/list-models

Defines the structure of the JSON response when listing Deepseek API models. It includes the schema for the 'list' object and the 'model' array, along with a concrete example of the expected data.

```json
{
  "object": "list",
  "data": [
    {
      "id": "string",
      "object": "model",
      "owned_by": "string"
    }
  ]
}
```

```json
{
  "object": "list",
  "data": [
    {
      "id": "deepseek-chat",
      "object": "model",
      "owned_by": "deepseek"
    },
    {
      "id": "deepseek-reasoner",
      "object": "model",
      "owned_by": "deepseek"
    }
  ]
}
```

--------------------------------

### List Models - C# Request

Source: https://api-docs.deepseek.com/api/list-models

This C# code snippet demonstrates how to list Deepseek API models. It uses 'HttpClient' to send a GET request to the API endpoint, setting the 'Authorization' and 'Accept' headers.

```csharp
using System;
using System.Net.Http;
using System.Threading.Tasks;

public class DeepseekApiClient
{
    public static async Task ListModelsAsync()
    {
        using (var client = new HttpClient())
        {
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Get,
                RequestUri = new Uri("https://api.deepseek.com/models")
            };

            request.Headers.Add("Authorization", "Bearer <TOKEN>");
            request.Headers.Add("Accept", "application/json");

            var response = await client.SendAsync(request);
            response.EnsureSuccessStatusCode();

            var responseBody = await response.Content.ReadAsStringAsync();
            Console.WriteLine(responseBody);
        }
    }

    public static async Task Main(string[] args)
    {
        await ListModelsAsync();
    }
}
```

--------------------------------

### Number and Integer Validation

Source: https://api-docs.deepseek.com/guides/tool_calls

Validates numeric and integer types with constraints such as const, default, minimum, maximum, exclusiveMinimum, exclusiveMaximum, and multipleOf. This example demonstrates rating validation.

```json
{
    "type": "object",
    "properties": {
        "score": {
            "type": "integer",
            "description": "A number from 1-5, which represents your rating, the higher, the better",
            "minimum": 1,
            "maximum": 5
        }
    },
    "required": ["score"],
    "additionalProperties": false
}
```

--------------------------------

### List Models - Node.js Request

Source: https://api-docs.deepseek.com/api/list-models

Shows how to fetch the list of Deepseek API models using Node.js. This snippet uses the built-in 'https' module to make a GET request, ensuring the Authorization and Accept headers are correctly set.

```javascript
const https = require('https');

const options = {
  hostname: 'api.deepseek.com',
  port: 443,
  path: '/models',
  method: 'GET',
  headers: {
    'Authorization': 'Bearer <TOKEN>',
    'Accept': 'application/json'
  }
};

const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    console.log(JSON.parse(data));
  });
}).on('error', (err) => {
  console.error('Error:', err);
});

req.end();
```

--------------------------------

### POST /beta/completions

Source: https://api-docs.deepseek.com/api/create-completion

The FIM (Fill-In-the-Middle) Completion API allows users to generate text completions. You must set `base_url="https://api.deepseek.com/beta"` to use this feature.

```APIDOC
## POST /beta/completions

### Description
Generates text completions using the Fill-In-the-Middle (FIM) approach.

### Method
POST

### Endpoint
https://api.deepseek.com/beta/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The ID of the model to use. Possible values: [`deepseek-chat`]
- **prompt** (string) - Required - The prompt to generate completions for. Default value: `Once upon a time, `
- **echo** (boolean) - Nullable - Echo back the prompt in addition to the completion.
- **frequency_penalty** (number) - Nullable - Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim. Default value: `0`
- **logprobs** (integer) - Nullable - Include the log probabilities on the `logprobs` most likely output tokens, as well as the chosen tokens. The maximum value for `logprobs` is 20.
- **max_tokens** (integer) - Nullable - The maximum number of tokens that can be generated in the completion.
- **presence_penalty** (number) - Nullable - Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics. Default value: `0`
- **stop** (object or string or array of strings) - Nullable - Up to 16 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
- **stream** (boolean) - Nullable - Whether to stream back partial progress. If set, tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a `data: [DONE]` message.
- **stream_options** (object) - Nullable - Options for streaming response. Only set this when you set `stream: true`.
    - **include_usage** (boolean) - If set, an additional chunk will be streamed before the `data: [DONE]` message. The `usage` field on this chunk shows the token usage statistics for the entire request, and the `choices` field will always be an empty array. All other chunks will also include a `usage` field, but with a null value.
- **suffix** (string) - Nullable - The suffix that comes after a completion of inserted text.
- **temperature** (number) - Nullable - What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. Default value: `1`
- **top_p** (number) - Nullable - An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered. Default value: `1`

### Request Example
```json
{
  "model": "deepseek-chat",
  "prompt": "The quick brown fox jumps over the lazy dog.",
  "max_tokens": 100,
  "temperature": 0.7
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the completion.
- **object** (string) - The type of object returned, usually "completion".
- **created** (integer) - The Unix timestamp of when the completion was created.
- **model** (string) - The ID of the model used for the completion.
- **choices** (array) - A list of completion choices.
    - **index** (integer) - The index of the choice.
    - **text** (string) - The generated text completion.
    - **logprobs** (object or null) - Log probabilities of the generated tokens.
    - **finish_reason** (string) - The reason the completion finished (e.g., "stop", "length").
- **usage** (object) - Token usage statistics for the request.
    - **prompt_tokens** (integer) - The number of tokens in the prompt.
    - **completion_tokens** (integer) - The number of tokens in the completion.
    - **total_tokens** (integer) - The total number of tokens used.

#### Response Example
```json
{
  "id": "cmpl-xxxxxxxxxxxxxxxxxxxxxxxx",
  "object": "completion",
  "created": 1677652288,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "text": " The lazy dog.",
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```
```

--------------------------------

### Strict Mode Tool Definition for Get Weather

Source: https://api-docs.deepseek.com/guides/tool_calls

Illustrates a tool definition in 'strict' mode for the 'get_weather' function using the Deepseek API. This ensures the model adheres precisely to the JSON schema requirements when generating tool calls. Note the `strict: true` parameter and the `additionalProperties: false` constraint on the object schema.

```json
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "strict": true,
        "description": "Get weather of a location, the user should supply a location first.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"],
            "additionalProperties": false
        }
    }
}

```

--------------------------------

### OpenAI Client Initialization (Python)

Source: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode

Initializes the OpenAI client using API key and base URL from environment variables. This client is used to interact with the Deepseek API.

```python
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL'),
)
```

--------------------------------

### New Completions API

Source: https://api-docs.deepseek.com/news/news0725

This endpoint provides general text completions using the Beta API. It supports features like FIM, function calling, and JSON output. The API is currently in beta and considered unstable.

```APIDOC
## POST /completions

### Description
This endpoint provides general text completions and supports advanced features such as Fill-in-the-Middle (FIM), function calling, and JSON output. This is a beta endpoint and may change.

### Method
POST

### Endpoint
https://api.deepseek.com/beta/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for completions.
- **prompt** (string) - Required - The prompt(s) to generate completions for.
- **temperature** (number) - Optional - Controls randomness. Lower values make the output more focused and deterministic.
- **top_p** (number) - Optional - Controls diversity via nucleus sampling.
- **n** (integer) - Optional - How many completions to generate for each prompt.
- **stream** (boolean) - Optional - Whether to stream back partial progress. If set, responses will be sent as server-sent events.
- **stop** (string or array) - Optional - Up to 4 sequences where the API will stop generating further tokens.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate in the completion.
- **presence_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
- **frequency_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the completion so far, decreasing the model's likelihood to repeat the same line verbatim.
- **best_of** (integer) - Optional - Generates best_of completions server-side and returns the best one. This parameter bypasses the n parameter.
- **logprobs** (integer) - Optional - Include the log probabilities of the top logprobs tokens that are, for example, the next token to be generated.
- **echo** (boolean) - Optional - Echo back the prompt in addition to the completion.
- **functions** (array) - Optional - A list of tools the model may call.
- **function_call** (string or object) - Optional - Controls how the model may call functions.

### Request Example
```json
{
  "model": "deepseek-coder-v2:instruct",
  "prompt": "Write a Python function to calculate the factorial of a number.\n```python\n",
  "temperature": 0.5,
  "max_tokens": 100
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the completion.
- **object** (string) - The type of object returned, usually "text_completion".
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - A list of completion choices.
  - **index** (integer) - The index of the choice.
  - **text** (string) - The generated text completion.
  - **logprobs** (object) - The log probabilities of the generated tokens (if requested).
  - **finish_reason** (string) - The reason the model stopped generating tokens (e.g., "stop", "length").
- **usage** (object) - Usage statistics for the completion.
  - **prompt_tokens** (integer) - The number of tokens in the prompt.
  - **completion_tokens** (integer) - The number of tokens in the completion.
  - **total_tokens** (integer) - The total number of tokens used.

#### Response Example
```json
{
  "id": "cmpl-7v3q2q6j3h7n7n7n7n7n7n7n7n",
  "object": "text_completion",
  "created": 1690888331,
  "model": "deepseek-coder-v2:instruct",
  "choices": [
    {
      "index": 0,
      "text": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)\n"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 27,
    "total_tokens": 42
  }
}
```
```

--------------------------------

### Context Caching Overview

Source: https://api-docs.deepseek.com/guides/kv_cache

Explains the default behavior of context caching, how cache hits are triggered by overlapping prefixes, and the general mechanism.

```APIDOC
## Context Caching Overview

The DeepSeek API Context Caching on Disk Technology is enabled by default for all users. It automatically constructs a disk cache for each user request. Subsequent requests with overlapping prefixes to previous ones will utilize the cache for the overlapping portion, resulting in a 'cache hit'. Only the repeated **prefix** part between two requests can trigger a 'cache hit'.
```

--------------------------------

### Sampling Parameters

Source: https://api-docs.deepseek.com/api/create-chat-completion

Controls the randomness and focus of the generated text. Use either `temperature` or `top_p`, but not both.

```APIDOC
## Sampling Parameters

### Description
Controls the randomness and focus of the generated text. Higher `temperature` values increase randomness, while lower values increase focus. `top_p` provides an alternative nucleus sampling method.

### Parameters

#### Temperature
- **temperature** (number) - Optional - A value between 0 and 2. Higher values (e.g., 0.8) make output more random; lower values (e.g., 0.2) make it more focused.

#### Top P
- **top_p** (number) - Optional - A value less than or equal to 1. An alternative to temperature sampling, considering tokens comprising the top `p` probability mass. Defaults to 1.

### Usage Note
It is generally recommended to alter either `temperature` or `top_p`, but not both simultaneously.
```

--------------------------------

### Mock Tool Functions and Call Map (Python)

Source: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode

Provides mock implementations for `get_date` and `get_weather` functions, simulating tool behavior. The `TOOL_CALL_MAP` dictionary maps tool names to their corresponding mock functions, enabling dynamic dispatch of tool calls.

```python
def get_date_mock():
    return "2025-12-01"

def get_weather_mock(location, date):
    return "Cloudy 7~13°C"

TOOL_CALL_MAP = {
    "get_date": get_date_mock,
    "get_weather": get_weather_mock
}
```

--------------------------------

### Enable JSON Output

Source: https://api-docs.deepseek.com/guides/json_mode

This section details the steps and considerations for enabling the JSON Output feature in the DeepSeek API. It explains how to set the `response_format` parameter, craft effective prompts, and manage token limits for successful JSON generation.

```APIDOC
## Enable JSON Output

### Description
To enable JSON Output, users should set the `response_format` parameter to `{'type': 'json_object'}`. It is also recommended to include the word "json" in the system or user prompt and provide an example of the desired JSON format. Ensure `max_tokens` is set reasonably to avoid truncation. Note that the API may occasionally return empty content, which is being optimized.

### Method
POST

### Endpoint
`/chat/completions`

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for chat completions (e.g., "deepseek-chat").
- **messages** (array) - Required - A list of messages comprising the conversation. Each message has a `role` (system, user, or assistant) and `content`.
- **response_format** (object) - Optional - Specifies the response format. Set to `{'type': 'json_object'}` to enable JSON output.
  - **type** (string) - Required - The type of response format, must be `json_object`.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate in the completion.

### Request Example
```python
import json
from openai import OpenAI

client = OpenAI(
    api_key="<your api key>",
    base_url="https://api.deepseek.com",
)

system_prompt = """
The user will provide some exam text. Please parse the \"question\" and \"answer\" and output them in JSON format.   

EXAMPLE INPUT:   
Which is the highest mountain in the world? Mount Everest.  

EXAMPLE JSON OUTPUT:  
{
    \"question\": \"Which is the highest mountain in the world?\",
    \"answer\": \"Mount Everest\"
}
"""

user_prompt = "Which is the longest river in the world? The Nile River."

messages = [{"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    response_format={
        'type': 'json_object'
    }
)

print(json.loads(response.choices[0].message.content))
```

### Response
#### Success Response (200)
- **choices** (array) - A list containing the generated completion(s).
  - **message** (object) - The message content.
    - **content** (string) - The generated JSON string.

#### Response Example
```json
{
    "question": "Which is the longest river in the world?",
    "answer": "The Nile River"
}
```
```

--------------------------------

### Invoke DeepSeek Model via Anthropic API (Python)

Source: https://api-docs.deepseek.com/guides/anthropic_api

This Python code snippet demonstrates how to initialize the Anthropic client and make a message creation request to the DeepSeek model. It specifies the model, maximum tokens, system prompt, and user message content. The output of the assistant's response is then printed.

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="deepseek-chat",
    max_tokens=1000,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hi, how are you?"
                }
            ]
        }
    ]
)
print(message.content)
```

--------------------------------

### Chat Completions API

Source: https://api-docs.deepseek.com/news/news0725

The updated Chat Completions API supports JSON output, function calling, chat prefix completion (Beta), and 8K max_tokens (Beta). These features are available for `deepseek-chat` and `deepseek-coder` models.

```APIDOC
## POST /chat/completions

### Description
This endpoint facilitates chat-based interactions and supports advanced features like generating JSON output, enabling function calls for external tool integration, performing chat prefix completion for more flexible output control, and increasing the maximum token limit to 8K.

### Method
POST

### Endpoint
/chat/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for chat completions (e.g., `deepseek-chat`, `deepseek-coder`).
- **messages** (array) - Required - An array of message objects representing the conversation history.
  - **role** (string) - Required - The role of the message sender (e.g., `system`, `user`, `assistant`).
  - **content** (string) - Required - The content of the message.
  - **prefix** (boolean) - Optional - Used with Chat Prefix Completion (Beta). Set to `True` for the last assistant message.
- **response_format** (object) - Optional - Used for JSON Output. Set to `{'type': 'json_object'}` to enforce JSON output.
  - **type** (string) - Required - The format type, must be `json_object`.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate. Defaults to 4096, can be up to 8192 in Beta.
- **temperature** (number) - Optional - Controls randomness. Lower values make output more deterministic.
- **stop** (string or array) - Optional - Sequences where the API will stop generating further tokens.

### Request Example
```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "user", "content": "Write a short story about a robot learning to love."}
  ],
  "response_format": {"type": "json_object"},
  "max_tokens": 1000
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the response.
- **object** (string) - Type of the object returned (e.g., `chat.completion`).
- **created** (integer) - Unix timestamp of when the response was created.
- **model** (string) - The model used for the response.
- **choices** (array) - An array of completion choices.
  - **index** (integer) - Index of the choice.
  - **message** (object) - The message object.
    - **role** (string) - The role of the message sender (`assistant`).
    - **content** (string) - The generated content.
  - **finish_reason** (string) - The reason the model stopped generating.
- **usage** (object) - Usage statistics for the request.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total tokens used.

#### Response Example
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"title\": \"The Tin Heart\", \"story\": \"Unit 734, a sanitation bot, processed data on human emotions daily. One day, observing a child hug a stray animal, a new subroutine flickered to life...\"}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 30,
    "completion_tokens": 50,
    "total_tokens": 80
  }
}
```
```

--------------------------------

### Log Probability Parameters

Source: https://api-docs.deepseek.com/api/create-chat-completion

Controls the retrieval of log probabilities for output tokens.

```APIDOC
## Log Probability Parameters

### Description
These parameters allow for the retrieval of log probabilities associated with the output tokens generated by the model.

### Parameters

#### Logprobs
- **logprobs** (boolean) - Optional, nullable - If set to `true`, returns the log probabilities of each output token within the `content` of the message.

#### Top Logprobs
- **top_logprobs** (integer) - Optional, nullable - An integer between 0 and 20. Specifies the number of most likely tokens to return at each token position, along with their associated log probabilities. Requires `logprobs` to be set to `true`.
```

--------------------------------

### Update Chat Completions API

Source: https://api-docs.deepseek.com/news/news0725

This endpoint allows for chat-based completions using the Beta API. It supports features like chat prefix completion, FIM, function calling, and JSON output. The API is currently in beta and considered unstable.

```APIDOC
## POST /chat/completions

### Description
This endpoint provides chat-based completions and supports advanced features such as chat prefix completion, Fill-in-the-Middle (FIM), function calling, and JSON output. This is a beta endpoint and may change.

### Method
POST

### Endpoint
https://api.deepseek.com/beta/chat/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for chat completions.
- **messages** (array) - Required - A list of messages comprising the conversation.
- **temperature** (number) - Optional - Controls randomness. Lower values make the output more focused and deterministic.
- **top_p** (number) - Optional - Controls diversity via nucleus sampling.
- **n** (integer) - Optional - How many chat completion choices to generate for each input message.
- **stream** (boolean) - Optional - Whether to stream back partial progress. If set, messages will be sent as server-sent events.
- **stop** (string or array) - Optional - Up to 4 sequences where the API will stop generating further tokens.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate in the chat completion.
- **presence_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
- **frequency_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the completion so far, decreasing the model's likelihood to repeat the same line verbatim.
- **logit_bias** (object) - Optional - A JSON object that maps tokens (specified by their token ID in UTF-8) to an associated bias value from -100 to 100. Use this to encourage or discourage the model from using specific tokens.
- **functions** (array) - Optional - A list of tools the model may call.
- **function_call** (string or object) - Optional - Controls how the model may call functions.

### Request Example
```json
{
  "model": "deepseek-coder-v2:instruct",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain the concept of a transformer model."}
  ],
  "temperature": 0.7,
  "max_tokens": 500
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the completion.
- **object** (string) - The type of object returned, usually "chat.completion".
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - A list of completion choices.
  - **index** (integer) - The index of the choice.
  - **message** (object) - The message content.
    - **role** (string) - The role of the author (e.g., "assistant").
    - **content** (string) - The text content of the message.
  - **finish_reason** (string) - The reason the model stopped generating tokens (e.g., "stop", "length").
- **usage** (object) - Usage statistics for the completion.
  - **prompt_tokens** (integer) - The number of tokens in the prompt.
  - **completion_tokens** (integer) - The number of tokens in the completion.
  - **total_tokens** (integer) - The total number of tokens used.

#### Response Example
```json
{
  "id": "chatcmpl-7v3q2q6j3h7n7n7n7n7n7n7n7n",
  "object": "chat.completion",
  "created": 1690888331,
  "model": "deepseek-coder-v2:instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "A transformer model is a type of neural network architecture that has become highly influential in natural language processing (NLP) tasks. It was introduced in the paper \"Attention Is All You Need\" by Vaswani et al. in 2017. The key innovation of the transformer is its reliance on the self-attention mechanism, which allows the model to weigh the importance of different words in the input sequence when processing a particular word, regardless of their distance from each other. This contrasts with previous architectures like Recurrent Neural Networks (RNNs) and Convolutional Neural Networks (CNNs) that process sequences sequentially or with limited context windows."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 100,
    "total_tokens": 125
  }
}
```
```

--------------------------------

### Model Details

Source: https://api-docs.deepseek.com/quick_start/pricing

Provides information about the different DeepSeek models, including their base URLs, versions, context lengths, maximum output tokens, and supported features like JSON output and tool calls.

```APIDOC
## Model Details

This section outlines the specifications and features of the available DeepSeek models.

### Models Available

*   **deepseek-chat**
    *   Base URL: `https://api.deepseek.com`
    *   Model Version: `DeepSeek-V3.2 (Non-thinking Mode)`
    *   Context Length: `128K`
    *   Max Output: `DEFAULT: 4K`, `MAXIMUM: 8K`
    *   Features: `Json Output`, `Tool Calls`, `Chat Prefix Completion（Beta）`

*   **deepseek-reasoner**
    *   Base URL: `https://api.deepseek.com`
    *   Model Version: `DeepSeek-V3.2 (Thinking Mode)`
    *   Context Length: `128K`
    *   Max Output: `DEFAULT: 32K`, `MAXIMUM: 64K`
    *   Features: `Json Output`, `Tool Calls`, `Chat Prefix Completion（Beta）`

*   **deepseek-reasoner(1)**
    *   Base URL: `https://api.deepseek.com/v3.2_speciale_expires_on_20251215`
    *   Model Version: `DeepSeek-V3.2-Speciale（Thinking Mode Only）`
    *   Context Length: `128K`
    *   Max Output: `DEFAULT: 128K`, `MAXIMUM: 128K`
    *   Features: `✗` (No JSON Output, Tool Calls, Chat Prefix Completion, FIM Completion)
    *   Note: This model is available until December 15, 2025, 15:59 UTC.

### Pricing

*   **1M INPUT TOKENS (CACHE HIT)**: `$0.028`
*   **1M INPUT TOKENS (CACHE MISS)**: `$0.28`
*   **1M OUTPUT TOKENS**: `$0.42`

### Deduction Rules

Expense is calculated as: `number of tokens × price`. Fees are deducted from your balance, prioritizing granted balance first. Prices are subject to change.
```

--------------------------------

### Multi-turn Conversation Handling

Source: https://api-docs.deepseek.com/guides/thinking_mode

Guidance on managing multi-turn conversations with DeepSeek models, including how to correctly pass conversation history and handle reasoning content.

```APIDOC
## Multi-turn Conversation

In multi-turn conversations, the model outputs both `reasoning_content` and `content` in each turn. For subsequent turns, the `reasoning_content` from previous turns is *not* automatically concatenated into the context. Only the final `content` from the assistant's previous response is included in the message history for the next user turn.

### API Example (Non-Streaming)

```python
from openai import OpenAI

client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# Turn 1
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages
)

reasoning_content = response.choices[0].message.reasoning_content
content = response.choices[0].message.content

# Turn 2
# Append the assistant's final content, not reasoning_content
messages.append({'role': 'assistant', 'content': content})
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages
)
# ... further turns ...
```

### API Example (Streaming)

```python
from openai import OpenAI

client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# Turn 1
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)

reasoning_content = ""
content = ""

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content += chunk.choices[0].delta.reasoning_content
    else:
        content += chunk.choices[0].delta.content

# Turn 2
# Append the assistant's final content, not reasoning_content
messages.append({"role": "assistant", "content": content})
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)
# ... further turns ...
```
```

--------------------------------

### Enable Thinking Mode via OpenAI SDK

Source: https://api-docs.deepseek.com/guides/thinking_mode

Demonstrates how to enable the thinking mode in the DeepSeek model when using the OpenAI SDK. This is achieved by passing the `thinking` parameter within the `extra_body` argument of the `client.chat.completions.create` method.

```python
response = client.chat.completions.create(
  model="deepseek-chat",
  # ...
  extra_body={"thinking": {"type": "enabled"}}
)

```

--------------------------------

### $ref and $def Schema

Source: https://api-docs.deepseek.com/guides/tool_calls

Enables modularization and reusability by defining reusable schema components in `$def` and referencing them with `$ref`. Also supports defining recursive structures.

```APIDOC
## $ref and $def Schema

### Description
You can use `$def` to define reusable modules and then use `$ref` to reference them, reducing schema repetition and enabling modularization. Additionally, `$ref` can be used independently to define recursive structures.

### Request Body Example
```json
{
    "type": "object",
    "properties": {
        "report_date": {
            "type": "string",
            "description": "The date when the report was published"
        },
        "authors": {
            "type": "array",
            "description": "The authors of the report",
            "items": {
                "$ref": "#/$def/author"
            }
        }
    },
    "required": ["report_date", "authors"],
    "additionalProperties": false,
    "$def": {
        "author": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Author's name"
                },
                "institution": {
                    "type": "string",
                    "description": "Author's institution"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Author's email"
                }
            },
            "additionalProperties": false,
            "required": ["name", "institution", "email"]
        }
    }
}
```
```

--------------------------------

### Tools and Tool Calls

Source: https://api-docs.deepseek.com/api/create-chat-completion

Defines the tools the model can use and controls which tool is invoked.

```APIDOC
## Tools and Tool Calls

### Description
This section details how to define and utilize tools, specifically functions, that the model can call. It also explains how to control which tool, if any, the model should use.

### Parameters

#### Tools
- **tools** (object[]) - Optional - A list of tools the model may call. Currently, only functions are supported. A maximum of 128 functions can be provided.
  - **type** (string) - Required - Must be `function`.
  - **function** (object) - Required - Defines the function details.
    - **description** (string) - Required - A description of what the function does, used by the model to choose when and how to call it.
    - **name** (string) - Required - The name of the function (max length 64 characters, allowed characters: a-z, A-Z, 0-9, underscores, dashes).
    - **parameters** (object) - Optional - The parameters the function accepts, described using JSON Schema. Omitting this defines a function with no parameters.
      - **property_name** (any) - Required (if parameters object is present) - Defines a parameter for the function.
    - **strict** (boolean) - Optional - If true, enforces strict JSON schema compliance for tool calls. Defaults to `false` (Beta feature).

#### Tool Choice
- **tool_choice** (object | string) - Optional - Controls which tool, if any, is called by the model.
  - If `string`: Can be `none`, `auto`, or `required`.
  - If `object`: Specifies a particular tool to force the model to call.
    - **type** (string) - Required - Must be `function`.
    - **function** (object) - Required - Specifies the function to call.
      - **name** (string) - Required - The name of the function to call.

### Default Behavior
- `none` is the default `tool_choice` when no tools are provided.
- `auto` is the default `tool_choice` when tools are provided.
```

--------------------------------

### Python Tool Calls in Thinking Mode for Deepseek API

Source: https://api-docs.deepseek.com/guides/thinking_mode

This Python script demonstrates how to perform tool calls using the Deepseek API in thinking mode. It defines tools, mocks their execution, and iteratively calls the chat completion API to resolve tool-dependent queries. The script requires the `openai` library and assumes the `DEEPSEEK_API_KEY` and `DEEPSEEK_BASE_URL` environment variables are set.

```python
import os
import json
from openai import OpenAI

# The definition of the tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "Get the current date",
            "parameters": { "type": "object", "properties": {} },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply the location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": { "type": "string", "description": "The city name" },
                    "date": { "type": "string", "description": "The date in format YYYY-mm-dd" },
                },
                "required": ["location", "date"]
            },
        }
    },
]

# The mocked version of the tool calls
def get_date_mock():
    return "2025-12-01"

def get_weather_mock(location, date):
    return "Cloudy 7~13°C"

TOOL_CALL_MAP = {
    "get_date": get_date_mock,
    "get_weather": get_weather_mock
}

def clear_reasoning_content(messages):
    for message in messages:
        if hasattr(message, 'reasoning_content'):
            message.reasoning_content = None

def run_turn(turn, messages):
    sub_turn = 1
    while True:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tools,
            extra_body={ "thinking": { "type": "enabled" } }
        )
        messages.append(response.choices[0].message)
        reasoning_content = response.choices[0].message.reasoning_content
        content = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls
        print(f"Turn {turn}.{sub_turn}\n{reasoning_content=}\n{content=}\n{tool_calls=}")
        # If there is no tool calls, then the model should get a final answer and we need to stop the loop
        if tool_calls is None:
            break
        for tool in tool_calls:
            tool_function = TOOL_CALL_MAP[tool.function.name]
            tool_result = tool_function(**json.loads(tool.function.arguments))
            print(f"tool result for {tool.function.name}: {tool_result}\n")
            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "content": tool_result,
            })
        sub_turn += 1

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url=os.environ.get('DEEPSEEK_BASE_URL'),
)

# The user starts a question
turn = 1
messages = [{
    "role": "user",
    "content": "How's the weather in Hangzhou Tomorrow"
}]
run_turn(turn, messages)

# The user starts a new question
turn = 2
messages.append({
    "role": "user",
    "content": "How's the weather in Hangzhou Tomorrow"
})

```

--------------------------------

### API Parameters and Output Structure

Source: https://api-docs.deepseek.com/guides/thinking_mode

Understand the input and output parameters for DeepSeek models, including those specific to Thinking Mode and its supported/unsupported features.

```APIDOC
## API Parameters

### Input Parameters

*   **`max_tokens`** (integer): The maximum length of the output, including the chain-of-thought (COT) part. The default is 32K, with a maximum of 64K.

### Output Parameters

The model's output includes the following fields when Thinking Mode is enabled:

*   **`reasoning_content`** (string): The content of the chain-of-thought reasoning. This is at the same level as `content` in the output structure.
*   **`content`** (string): The content of the final answer.
*   **`tool_calls`** (array): Any tool calls made by the model.

### Supported Features

*   Json Output
*   Tool Calls
*   Chat Completion
*   Chat Prefix Completion (Beta)

### Not Supported Features

*   FIM (Beta)

### Not Supported Parameters

The following parameters are not supported and will either have no effect or cause an error:

*   `temperature`
*   `top_p`
*   `presence_penalty`
*   `frequency_penalty`
*   `logprobs`
*   `top_logprobs`

*Note*: Setting `temperature`, `top_p`, `presence_penalty`, or `frequency_penalty` will not raise an error but will have no effect. Setting `logprobs` or `top_logprobs` will trigger an error.
```

--------------------------------

### AnyOf Schema

Source: https://api-docs.deepseek.com/guides/tool_calls

Allows a field to match any one of the provided schemas, enabling flexibility for fields that can accept multiple data types or formats.

```APIDOC
## AnyOf Schema

### Description
Matches any one of the provided schemas, allowing fields to accommodate multiple valid formats. For example, a user's account could be either an email address or a phone number.

### Request Body Example
```json
{
    "type": "object",
    "properties": {
    "account": {
        "anyOf": [
            { "type": "string", "format": "email", "description": "User's email address" },
            { "type": "string", "pattern": "^\\d{11}$", "description": "User's 11-digit phone number" }
        ]
    }
  }
}
```
```

--------------------------------

### POST /v1/chat/completions

Source: https://api-docs.deepseek.com/api/create-chat-completion

Creates a message on behalf of the model and returns a chat completion. This endpoint is used to generate text-based responses in a conversational format.

```APIDOC
## POST /v1/chat/completions

### Description
This endpoint creates a message on behalf of the model and returns a chat completion. It is used to generate text-based responses in a conversational format, supporting both standard and streaming responses.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Query Parameters
- **stream** (boolean) - Optional - If set to `true`, streaming of chunks in the<bos> format is enabled.

#### Request Body
- **model** (string) - Required - The model to use for the chat completion.
- **messages** (object[]) - Required - A list of messages comprising the conversation so far.
- **temperature** (number) - Optional - Controls randomness. Lower values make the output more focused and deterministic.
- **top_p** (number) - Optional - Controls diversity via nucleus sampling.
- **n** (integer) - Optional - How many chat completion choices to generate for each input message.
- **stream_options** (object) - Optional - Streaming related options.
  - **include_usage** (boolean) - Optional - If set, Usage fields will be included in the stream output.
- **stop** (string | string[]) - Optional - Up to 4 sequences where the API will stop generating further tokens.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate in the completion.
- **presence_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
- **frequency_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
- **logit_bias** (object) - Optional - A map of token logits to reduce the probability of generating. Used to supply text that the model should avoid.
- **tool_choice** (string | object) - Optional - Controls whether the model is allowed to call a tool.
- **tools** (object[]) - Optional - A list of tools the model may call.
  - **type** (string) - Required - The type of the tool. Currently, `function` is supported.
  - **function** (object) - Required - The definition of the function that the tool calls.
    - **name** (string) - Required - The name of the function to call.
    - **description** (string) - Optional - A description of what the function does, used to match tool calls with functions.
    - **parameters** (object) - Optional - The parameters the function accepts, in JSON schema format.

### Request Example
```json
{
  "model": "deepseek-coder",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello, who are you?"
    }
  ]
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the chat completion.
- **choices** (object[]) - A list of chat completion choices.
  - **finish_reason** (string) - The reason the model stopped generating tokens.
  - **index** (integer) - The index of the choice in the list of choices.
  - **message** (object) - A chat completion message generated by the model.
    - **content** (string | null) - The contents of the message.
    - **reasoning_content** (string | null) - For `deepseek-reasoner` model only. The reasoning contents of the assistant message, before the final answer.
    - **tool_calls** (object[]) - The tool calls generated by the model.
      - **id** (string) - The ID of the tool call.
      - **type** (string) - The type of the tool. Currently, only `function` is supported.
      - **function** (object) - The function that the model called.
        - **name** (string) - The name of the function to call.
        - **arguments** (string) - The arguments to call the function with, as generated by the model in JSON format.
    - **role** (string) - The role of the author of this message.
  - **logprobs** (object | null) - Log probability information for the choice.
    - **content** (object[]) - A list of message content tokens with log probability information.
      - **token** (string) - The token.
      - **logprob** (number) - The log probability of this token.
      - **bytes** (integer[]) - UTF-8 bytes representation of the token.
    - **top_logprobs** (object[]) - List of the most likely tokens and their log probability.
      - **token** (string) - The token.
      - **logprob** (number) - The log probability of this token.
      - **bytes** (integer[]) - UTF-8 bytes representation of the token.
  - **reasoning_content** (object[]) - A list of message content tokens with log probability information.
    - **token** (string) - The token.
    - **logprob** (number) - The log probability of this token.
    - **bytes** (integer[]) - UTF-8 bytes representation of the token.
    - **top_logprobs** (object[]) - List of the most likely tokens and their log probability.
      - **token** (string) - The token.
      - **logprob** (number) - The log probability of this token.
      - **bytes** (integer[]) - UTF-8 bytes representation of the token.
- **created** (integer) - Unix timestamp (in seconds) of when the completion was created.
- **model** (string) - The model that was used for the completion.
- **system_fingerprint** (string) - This fingerprint identifies the model version. This may be used to rebroadcast a previous completion.
- **usage** (object) - Usage statistics for the completion request.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total number of tokens in the request and completion.

#### Response Example
```json
{
  "id": "chatcmpl-7vZ0j2Q3",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I am a helpful assistant."
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "created": 1692076800,
  "model": "deepseek-coder",
  "system_fingerprint": "fp_94123845",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```
```

--------------------------------

### Configure Environment Variables for Anthropic API

Source: https://api-docs.deepseek.com/guides/anthropic_api

Set the necessary environment variables to configure the Anthropic SDK to point to the DeepSeek API. This includes setting the base URL for the API and your DeepSeek API key.

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY=${DEEPSEEK_API_KEY}
```

--------------------------------

### Text Completion API

Source: https://api-docs.deepseek.com/api/create-completion

This endpoint allows you to generate text completions based on a provided prompt and model.

```APIDOC
## POST /beta/chat/completions

### Description
This endpoint generates text completions using a specified model. You can control the output with various parameters such as temperature, max_tokens, and stop sequences.

### Method
POST

### Endpoint
https://api.deepseek.com/beta/chat/completions

### Parameters
#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use for completion (e.g., "deepseek-chat").
- **prompt** (string) - Required - The prompt(s) to generate completions for.
- **echo** (boolean) - Optional - Whether to echo the prompt in the completion.
- **frequency_penalty** (number) - Optional - Controls penalty for frequent tokens.
- **logprobs** (integer) - Optional - The number of log probabilities to return alongside the completion.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate.
- **presence_penalty** (number) - Optional - Controls penalty for existing tokens.
- **stop** (string or array of strings) - Optional - Sequences where the API will stop generating further tokens.
- **stream** (boolean) - Optional - Whether to stream back partial progress. If set, timeout is not ignored.
- **stream_options** (object) - Optional - Options for streaming.
- **suffix** (string) - Optional - The suffix that can be appended after generating the completion.
- **temperature** (number) - Optional - Controls randomness. Lower is more deterministic.
- **top_p** (number) - Optional - Controls diversity via nucleus sampling.

### Request Example
```json
{
  "model": "deepseek-chat",
  "prompt": "Once upon a time, ",
  "echo": false,
  "frequency_penalty": 0,
  "logprobs": 0,
  "max_tokens": 1024,
  "presence_penalty": 0,
  "stop": null,
  "stream": false,
  "stream_options": null,
  "suffix": null,
  "temperature": 1,
  "top_p": 1
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the completion.
- **choices** (array) - The list of completion choices.
  - **finish_reason** (string) - The reason the model stopped generating tokens.
  - **index** (integer) - The index of the choice.
  - **logprobs** (object) - Log probabilities for the completion.
  - **text** (string) - The generated text.
- **created** (integer) - The Unix timestamp of creation.
- **model** (string) - The model used.
- **system_fingerprint** (string) - Backend configuration fingerprint.
- **object** (string) - The object type (always "text_completion").
- **usage** (object) - Usage statistics.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **prompt_cache_hit_tokens** (integer) - Tokens from prompt cache hit.
  - **prompt_cache_miss_tokens** (integer) - Tokens from prompt cache miss.
  - **total_tokens** (integer) - Total tokens used.
  - **completion_tokens_details** (object) - Breakdown of completion tokens.
    - **reasoning_tokens** (integer) - Tokens generated for reasoning.

#### Response Example
```json
{
  "id": "string",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": {
        "text_offset": [
          0
        ],
        "token_logprobs": [
          0
        ],
        "tokens": [
          "string"
        ],
        "top_logprobs": [
          {}
        ]
      },
      "text": "string"
    }
  ],
  "created": 0,
  "model": "string",
  "system_fingerprint": "string",
  "object": "text_completion",
  "usage": {
    "completion_tokens": 0,
    "prompt_tokens": 0,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 0,
    "total_tokens": 0,
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```
```

--------------------------------

### Clear Reasoning Content from History (Python)

Source: https://api-docs.deepseek.com/guides/thinking_mode

This function, `clear_reasoning_content`, is recommended to be called at the beginning of new turns (e.g., Turn 2) to optimize network bandwidth. By removing the `reasoning_content` from previous turns, the payload sent to the API is reduced without losing essential conversational data.

```python
clear_reasoning_content(messages)

```

--------------------------------

### Chat Completion

Source: https://api-docs.deepseek.com/api/create-chat-completion

This endpoint creates a chat completion model response for the provided prompts. It supports streaming responses for real-time updates.

```APIDOC
## POST /v1/chat/completions

### Description
Creates a chat completion model response for the provided prompts. Supports streaming responses.

### Method
POST

### Endpoint
/v1/chat/completions

### Parameters
#### Request Body
- **model** (string) - Required - The model ID to use for completion.
- **messages** (array) - Required - A list of messages comprising the conversation.
  - **role** (string) - Required - The role of the author. Possible values: `system`, `user`, `assistant`.
  - **content** (string) - Required - The content of the message.
- **stream** (boolean) - Optional - Whether to stream back chunks of the completion in real-time.
- **temperature** (number) - Optional - Controls randomness. Higher values increase randomness.
- **top_p** (number) - Optional - Controls diversity via nucleus sampling.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate.

### Request Example
```json
{
  "model": "deepseek-coder",
  "messages": [
    {
      "role": "user",
      "content": "Write a python function to calculate fibonacci sequence."
    }
  ],
  "stream": false
}
```

### Response
#### Success Response (200)
- **id** (string) - A unique identifier for the chat completion.
- **choices** (array) - A list of chat completion choices.
  - **message** (object) - The message content and role.
    - **content** (string) - The content of the message.
    - **role** (string) - The role of the author.
  - **finish_reason** (string) - The reason the model stopped generating tokens.
- **created** (integer) - The Unix timestamp of when the chat completion was created.
- **model** (string) - The model used for the chat completion.
- **object** (string) - The object type, always `chat.completion`.
- **usage** (object) - Usage statistics for the completion request.
  - **completion_tokens** (integer) - Number of tokens in the generated completion.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **total_tokens** (integer) - Total number of tokens used in the request.

#### Response Example
```json
{
  "id": "930c60df-bf64-41c9-a88e-3ec75f81e00e",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "Hello! How can I help you today?",
        "role": "assistant"
      }
    }
  ],
  "created": 1705651092,
  "model": "deepseek-chat",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 10,
    "prompt_tokens": 16,
    "total_tokens": 26
  }
}
```

#### Streaming Response Example (text/event-stream)
```
{
  "id": "chatcmpl-123",
  "object": "chat.completion.chunk",
  "created": 1677711000,
  "model": "deepseek-coder",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "Sure, here is a Python function"
      },
      "finish_reason": null
    }
  ]
}
{
  "id": "chatcmpl-123",
  "object": "chat.completion.chunk",
  "created": 1677711000,
  "model": "deepseek-coder",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": " for calculating the Fibonacci sequence:"
      },
      "finish_reason": null
    }
  ]
}
{
  "id": "chatcmpl-123",
  "object": "chat.completion.chunk",
  "created": 1677711000,
  "model": "deepseek-coder",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "\n```python\ndef fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n```"
      },
      "finish_reason": "stop"
    }
  ]
}
```
```

--------------------------------

### Configure Claude Code for V3.1-Terminus

Source: https://api-docs.deepseek.com/guides/comparison_testing

This command sets the `ANTHROPIC_BASE_URL` environment variable to point to the DeepSeek V3.1-Terminus API endpoint for Anthropic compatibility. This allows users to access the V3.1-Terminus model when using Anthropic's tools or SDKs.

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/v3.1_terminus_expires_on_20251015/anthropic

```

--------------------------------

### Continue a Conversation Turn (Python)

Source: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode

Shows how to continue an existing conversation by appending a new user message to the `messages` list and calling `run_turn` again. This allows for multi-turn interactions.

```python
# The user starts a new question
turn = 2
messages.append({
    "role": "user",
    "content": "How's the weather in Hangzhou Tomorrow"
})
run_turn(turn, messages)
```

--------------------------------

### Enable Thinking Mode

Source: https://api-docs.deepseek.com/guides/thinking_mode

Learn how to enable the thinking mode in DeepSeek models to leverage chain-of-thought reasoning for improved response accuracy.

```APIDOC
## Enable Thinking Mode

Thinking mode allows the DeepSeek model to output a chain-of-thought reasoning before providing the final answer, enhancing accuracy. This mode can be enabled using one of the following methods:

1.  **Set the `model` parameter**: Use the specific model designed for reasoning.
    ```json
    {
      "model": "deepseek-reasoner"
    }
    ```

2.  **Set the `thinking` parameter**: Use a general parameter to enable thinking.
    ```json
    {
      "thinking": {"type": "enabled"}
    }
    ```

### OpenAI SDK Usage

When using the OpenAI SDK, the `thinking` parameter needs to be passed within the `extra_body` argument:

```python
from openai import OpenAI

client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
  model="deepseek-chat",
  # ... other parameters ...
  extra_body={"thinking": {"type": "enabled"}}
)
```
```

--------------------------------

### FIM Completion Endpoint

Source: https://api-docs.deepseek.com/guides/fim_completion

This endpoint allows for Fill-In-the-Middle completion. You provide a prompt (prefix) and an optional suffix, and the model generates the text that fits in between. This is particularly useful for code completion tasks.

```APIDOC
## POST /beta/completions

### Description
Generates text or code completion by filling in the middle of a given prefix and suffix.

### Method
POST

### Endpoint
`https://api.deepseek.com/beta/completions`

### Parameters
#### Query Parameters
- **model** (string) - Required - The model to use for completion (e.g., "deepseek-chat").
- **prompt** (string) - Required - The beginning text or code snippet (prefix).
- **suffix** (string) - Optional - The ending text or code snippet.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate. Defaults to 4096.

### Request Example
```json
{
  "model": "deepseek-chat",
  "prompt": "def fib(a):",
  "suffix": "    return fib(a-1) + fib(a-2)",
  "max_tokens": 128
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the completion.
- **object** (string) - Type of object returned (e.g., "completion").
- **created** (integer) - Timestamp of creation.
- **model** (string) - The model used for completion.
- **choices** (array) - An array of completion choices.
  - **index** (integer) - Index of the choice.
  - **text** (string) - The generated text or code completion.
  - **logprobs** (null) - Log probabilities (currently null).
  - **finish_reason** (string) - The reason the model stopped generating text (e.g., "stop", "length").
- **usage** (object) - Information about token usage.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total number of tokens used.

#### Response Example
```json
{
  "id": "cmpl-xxxxxxxxxxxxxxxxxxxxxxxx",
  "object": "completion",
  "created": 1700000000,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "text": "\n    if a <= 1:\n        return a\n",
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```
```

--------------------------------

### Chat Completions API

Source: https://api-docs.deepseek.com/index

This endpoint allows you to invoke the chat completion model, similar to OpenAI's chat completion endpoint. You can specify the model, messages, and whether to stream the response.

```APIDOC
## POST /chat/completions

### Description
Invokes the chat completion model to generate responses based on the provided messages. Supports both non-stream and stream responses.

### Method
POST

### Endpoint
https://api.deepseek.com/chat/completions

### Parameters
#### Header Parameters
- **Content-Type** (string) - Required - `application/json`
- **Authorization** (string) - Required - `Bearer YOUR_API_KEY`

#### Request Body
- **model** (string) - Required - The model to use for chat completions (e.g., `deepseek-chat`, `deepseek-coder`).
- **messages** (array) - Required - An array of message objects, each with a `role` (`system`, `user`, or `assistant`) and `content`.
- **stream** (boolean) - Optional - If `true`, the response will be streamed. Defaults to `false`.

### Request Example
```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."}ె,
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}
```

### Response
#### Success Response (200)
- **id** (string) - The ID of the completion.
- **object** (string) - The type of object returned, e.g. `chat.completion`.
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - A list of completion choices.
  - **index** (integer) - The index of the choice.
  - **message** (object) - The message object.
    - **role** (string) - The role of the message sender (`assistant`).
    - **content** (string) - The content of the assistant's message.
  - **finish_reason** (string) - The reason the model finished generating tokens (e.g., `stop`, `length`).
- **usage** (object) - Usage statistics for the completion.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total number of tokens used.

#### Response Example
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```
```

--------------------------------

### Tool Calls in Thinking Mode

Source: https://api-docs.deepseek.com/guides/thinking_mode

Details on how to integrate tool calls within DeepSeek's Thinking Mode, allowing the model to use external tools during its reasoning process.

```APIDOC
## Tool Calls

DeepSeek models support tool calls within Thinking Mode. This enables the model to perform multiple turns of reasoning and tool usage before generating a final answer, potentially improving response quality.

### Process Overview

*   **Multi-turn Reasoning and Tool Calls**: During a single user query, the model may engage in several internal steps involving reasoning and calling tools. The user needs to resubmit the `reasoning_content` received from the model back to the API in subsequent requests within the same turn to allow the model to continue its thought process.
*   **Starting a New User Question**: When a new, independent user question is asked (e.g., Turn 2.1 after a previous multi-step answer), the `reasoning_content` from the *previous* user turn should be discarded. Only the standard message history (user prompts and assistant responses) should be sent. If `reasoning_content` is incorrectly included in a new, independent query, the API will ignore it.

### Compatibility Notice

Incorrectly handling the `reasoning_content` during tool-use interactions in Thinking Mode can lead to a 400 error from the API. Ensure that `reasoning_content` is correctly passed back to the API during iterative reasoning steps within a single query. Refer to the provided sample code for the correct implementation.
```

--------------------------------

### POST /chat/completions

Source: https://api-docs.deepseek.com/zh-cn/api/create-chat-completion

This endpoint allows you to generate chat completions using various models. You can specify system and user messages, model parameters like temperature and max tokens, and more.

```APIDOC
## POST /chat/completions

### Description
This endpoint generates chat completions based on provided messages and model configurations. It supports various parameters to control the generation process, such as `temperature`, `max_tokens`, and `stream`.

### Method
POST

### Endpoint
https://api.deepseek.com/chat/completions

### Parameters
#### Header Parameters
- **Authorization** (string) - Required - Bearer token for authentication.
- **Content-Type** (string) - Required - Must be `application/json`.
- **Accept** (string) - Required - Must be `application/json`.

#### Request Body
- **messages** (array) - Required - An array of message objects, each with a `role` (system, user, or assistant) and `content`.
- **model** (string) - Required - The model to use for chat completion (e.g., `deepseek-chat`).
- **thinking** (object) - Optional - Configuration for thinking process, usually `{"type": "disabled"}`.
- **frequency_penalty** (number) - Optional - Controls how much to penalize new tokens based on their existing frequency in the text so far. Defaults to 0.
- **max_tokens** (integer) - Optional - The maximum number of tokens to generate in the completion. Defaults to 4096.
- **presence_penalty** (number) - Optional - Controls how much to penalize new tokens based on whether they appear in the text so far. Defaults to 0.
- **response_format** (object) - Optional - Specifies the format of the response. `{"type": "text"}` is common.
- **stop** (string or array) - Optional - Up to 4 sequences where the API will stop generating further tokens.
- **stream** (boolean) - Optional - Whether to stream back partial progress. Defaults to `false`.
- **stream_options** (object) - Optional - Options for streaming.
- **temperature** (number) - Optional - Controls randomness. Lower values make the output more deterministic. Defaults to 1.
- **top_p** (number) - Optional - Controls diversity via nucleus sampling. Defaults to 1.
- **tools** (array) - Optional - A list of tools the model may call.
- **tool_choice** (string) - Optional - Controls how the model is allowed to use the provided tools. Defaults to `none`.
- **logprobs** (boolean) - Optional - Whether to return log probabilities of the output tokens. Defaults to `false`.
- **top_logprobs** (integer) - Optional - An integer specifying the number of log_prob results to return for each output token.

### Request Example
```json
{
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "thinking": {
    "type": "disabled"
  },
  "frequency_penalty": 0,
  "max_tokens": 4096,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": null,
  "stream": false,
  "stream_options": null,
  "temperature": 1,
  "top_p": 1,
  "tools": null,
  "tool_choice": "none",
  "logprobs": false,
  "top_logprobs": null
}
```

### Response
#### Success Response (200)
- **id** (string) - Unique identifier for the completion.
- **object** (string) - Type of object, e.g., `chat.completion`.
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - An array of completion choices.
  - **index** (integer) - Index of the choice.
  - **message** (object) - The generated message.
    - **role** (string) - Role of the message sender (e.g., `assistant`).
    - **content** (string) - The content of the message.
  - **finish_reason** (string) - The reason the generation finished (e.g., `stop`, `length`).
- **usage** (object) - Usage statistics for the completion.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total number of tokens used.

#### Response Example
```json
{
  "choices": [
    {
      "delta": {
        "content": " I can assist you today?",
        "role": "assistant"
      },
      "finish_reason": null,
      "index": 0,
      "logprobs": null
    }
  ],
  "created": 1718345013,
  "id": "1f633d8bfc032625086f14113c411638",
  "model": "deepseek-chat",
  "object": "chat.completion.chunk",
  "system_fingerprint": "fp_a49d71b8a1"
}
```
```

--------------------------------

### Invoke Chat API via Curl

Source: https://api-docs.deepseek.com/index

This snippet demonstrates how to invoke the DeepSeek chat API using a curl command. It requires setting the Authorization header with your API key and providing the model and messages in the request body. The `stream` parameter can be set to `true` for streaming responses.

```curl
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY}" \
  -d '{
        "model": "deepseek-chat",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
        ],
        "stream": false
      }'

```

--------------------------------

### Invoke V3.1-Terminus API with Curl

Source: https://api-docs.deepseek.com/guides/comparison_testing

This snippet demonstrates how to invoke the DeepSeek V3.1-Terminus API using curl. It requires setting the Authorization header with your API key and sends a chat completion request. The output includes the model name, allowing verification of the V3.1-Terminus model usage.

```shell
curl https://api.deepseek.com/v3.1_terminus_expires_on_20251015/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${DEEPSEEK_API_KEY}" \
  -d '{
        "model": "deepseek-chat",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
        ],
        "stream": false
      }'

```

--------------------------------

### Streaming API Call with Thinking Mode (Python)

Source: https://api-docs.deepseek.com/guides/thinking_mode

Illustrates how to perform a streaming API call to the DeepSeek model with thinking mode enabled using Python. The code iterates through the streamed chunks to reconstruct the `reasoning_content` and the final `content`, managing multi-turn conversations correctly.

```python
from openai import OpenAI
client = OpenAI(api_key="<DeepSeek API Key>", base_url="https://api.deepseek.com")

# Turn 1
messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)

reasoning_content = ""
content = ""

for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        reasoning_content += chunk.choices[0].delta.reasoning_content
    else:
        content += chunk.choices[0].delta.content

# Turn 2
messages.append({"role": "assistant", "content": content})
messages.append({'role': 'user', 'content': "How many Rs are there in the word 'strawberry'?"})
response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=messages,
    stream=True
)
# ...

```

--------------------------------

### Tool Calls - Strict Mode Configuration

Source: https://api-docs.deepseek.com/guides/tool_calls

Details on how to enable and configure 'strict' mode for Tool Calls, ensuring the model adheres precisely to the Function's JSON schema. This mode is available in Beta.

```APIDOC
## Beta API Endpoint for Strict Mode

### Description
This section describes how to enable and use the 'strict' mode for Tool Calls, which enforces adherence to the JSON schema provided for functions. This feature is in Beta.

### Method
POST

### Endpoint
https://api.deepseek.com/beta

### Parameters
#### Query Parameters
None

#### Request Body
In addition to the standard chat completion parameters, the `tools` parameter requires specific configuration for strict mode:
- **tools** (array) - A list of tool definitions.
  - **type** (string) - Required - The type of the tool (e.g., "function").
  - **function** (object) - Required - The function definition.
    - **name** (string) - Required - The name of the function.
    - **strict** (boolean) - Required - Set to `true` to enable strict mode for this function.
    - **description** (string) - Optional - A description of what the function does.
    - **parameters** (object) - Required - The JSON schema describing the function's parameters.
      - **type** (string) - Required - The type of the parameter (e.g., "object").
      - **properties** (object) - Optional - An object defining the properties of the parameter.
      - **required** (array) - Optional - An array of strings listing the required parameters.
      - **additionalProperties** (boolean) - Required for objects - Must be set to `false`.

### Request Example (Strict Mode Tool Definition)
```json
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "strict": true,
        "description": "Get weather of a location, the user should supply a location first.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                }
            },
            "required": ["location"],
            "additionalProperties": false
        }
    }
}
```

### Supported JSON Schema Types in `strict` Mode
- object
- string
- number
- integer
- boolean
- array
- enum
- anyOf

### Object Definition Constraints in `strict` Mode
For objects, all properties within `properties` must be listed in the `required` array, and `additionalProperties` must be set to `false`.

### Response
#### Success Response (200)
Standard chat completion response. If the provided JSON schema is invalid or unsupported, an error message will be returned.

#### Error Response
- **code** (integer) - Error code.
- **message** (string) - Error message detailing the schema validation failure or unsupported type.

#### Response Example (Schema Error)
```json
{
  "code": 400,
  "message": "Invalid JSON schema provided for function 'get_weather'. Property 'zip_code' is not defined and additionalProperties is set to false."
}
```
```

--------------------------------

### Run Conversational Turn with Deepseek API (Python)

Source: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode

The core function for managing a conversational turn with the Deepseek API. It sends messages to the API, processes the response including tool calls, executes the required tools using `TOOL_CALL_MAP`, and appends tool results back to the message history. The loop continues until the model provides a final answer (no tool calls).

```python
def run_turn(turn, messages):
    sub_turn = 1
    while True:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=messages,
            tools=tools,
            extra_body={ "thinking": { "type": "enabled" } }
        )
        messages.append(response.choices[0].message)
        reasoning_content = response.choices[0].message.reasoning_content
        content = response.choices[0].message.content
        tool_calls = response.choices[0].message.tool_calls
        print(f"Turn {turn}.{sub_turn}\n{reasoning_content=}\n{content=}\n{tool_calls=}")
        if tool_calls is None:
            break
        for tool in tool_calls:
            tool_function = TOOL_CALL_MAP[tool.function.name]
            tool_result = tool_function(**json.loads(tool.function.arguments))
            print(f"tool result for {tool.function.name}: {tool_result}\n")
            messages.append({
                "role": "tool",
                "tool_call_id": tool.id,
                "content": tool_result,
            })
        sub_turn += 1
```

--------------------------------

### Chat Completion Chunk Structure (JSON)

Source: https://api-docs.deepseek.com/api/create-chat-completion

This JSON object represents a single chunk of a chat completion response. It includes metadata like the model, creation timestamp, and a unique identifier. The 'choices' array contains the generated message fragments, detailing the token, its log probability, and its byte representation.

```json
{
  "id": "1f633d8bfc032625086f14113c411638",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "",
        "role": "assistant"
      },
      "finish_reason": null,
      "logprobs": null
    }
  ],
  "created": 1718345013,
  "model": "deepseek-chat",
  "system_fingerprint": "fp_a49d71b8a1",
  "object": "chat.completion.chunk",
  "usage": null
}
```

```json
{
  "choices": [
    {
      "delta": {
        "content": "Hello",
        "role": "assistant"
      },
      "finish_reason": null,
      "index": 0,
      "logprobs": null
    }
  ],
  "created": 1718345013,
  "id": "1f633d8bfc032625086f14113c411638",
  "model": "deepseek-chat",
  "object": "chat.completion.chunk",
  "system_fingerprint": "fp_a49d71b8a1"
}
```

```json
{
  "choices": [
    {
      "delta": {
        "content": "!",
        "role": "assistant"
      },
      "finish_reason": null,
      "index": 0,
      "logprobs": null
    }
  ],
  "created": 1718345013,
  "id": "1f633d8bfc032625086f14113c411638",
  "model": "deepseek-chat",
  "object": "chat.completion.chunk",
  "system_fingerprint": "fp_a49d71b8a1"
}
```

```json
{
  "choices": [
    {
      "delta": {
        "content": " How",
        "role": "assistant"
      },
      "finish_reason": null,
      "index": 0,
      "logprobs": null
    }
  ],
  "created": 1718345013,
  "id": "1f633d8bfc032625086f14113c411638",
  "model": "deepseek-chat",
  "object": "chat.completion.chunk",
  "system_fingerprint": "fp_a49d71b8a1"
}
```

--------------------------------

### Chat Completion API

Source: https://api-docs.deepseek.com/api/create-chat-completion

This endpoint allows you to interact with Deepseek's chat models to generate responses based on a conversation history.

```APIDOC
## POST /chat/completions

### Description
Generates a model response from the model's messages.

### Method
POST

### Endpoint
/chat/completions

### Parameters
#### Request Body
- **messages** (object[]) - Required - An array of message objects representing the conversation history. Each message object can be a system, user, assistant, or tool message.
- **model** (string) - Required - The ID of the model to use (e.g., `deepseek-chat`, `deepseek-reasoner`).
- **thinking** (object) - Optional - Controls the switch between thinking and non-thinking mode. Possible values: `enabled`, `disabled`.
- **frequency_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency. Default: `0`.
- **max_tokens** (integer) - Optional - The maximum number of tokens that can be generated in the chat completion.
- **presence_penalty** (number) - Optional - Number between -2.0 and 2.0. Positive values penalize new tokens based on their appearance in the text so far. Default: `0`.
- **response_format** (object) - Optional - An object specifying the format that the model must output. Currently supports `{"type": "json_object"}` for JSON Output.
- **stop** (object or string or array) - Optional - Up to 16 sequences where the API will stop generating further tokens.
- **stream** (boolean) - Optional - If set, partial message deltas will be sent as server-sent events.
- **stream_options** (object) - Optional - Options for streaming response. Only set this when `stream` is true. Contains `include_usage` (boolean).
- **temperature** (number) - Optional - Number between 0 and 2. Controls randomness. Default: `1`.

### Request Example
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello, world!"
    }
  ],
  "model": "deepseek-chat",
  "stream": false
}
```

### Response
#### Success Response (200)
- **id** (string) - The unique identifier for the chat completion.
- **object** (string) - The type of object, usually `chat.completion`.
- **created** (integer) - Unix timestamp of when the completion was created.
- **model** (string) - The model used for the completion.
- **choices** (array) - A list of completion choices.
  - **index** (integer) - Index of the choice.
  - **message** (object) - The message content and role.
    - **role** (string) - The role of the author of the message (`assistant`).
    - **content** (string) - The content of the message.
  - **finish_reason** (string) - The reason the model stopped generating tokens (e.g., `stop`, `length`).
- **usage** (object) - Usage statistics for the request.
  - **prompt_tokens** (integer) - Number of tokens in the prompt.
  - **completion_tokens** (integer) - Number of tokens in the completion.
  - **total_tokens** (integer) - Total tokens used.

#### Response Example
```json
{
  "id": "chatcmpl-7zM5d028u6aC8a9Q90aP0b3b5b1b5b",
  "object": "chat.completion",
  "created": 1694708221,
  "model": "deepseek-chat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello there! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 12,
    "total_tokens": 22
  }
}
```
```

--------------------------------

### String Schema

Source: https://api-docs.deepseek.com/guides/tool_calls

Defines how string values are validated within API requests and responses. Supports pattern matching with regular expressions and predefined formats like email or IP addresses.

```APIDOC
## String Schema

### Description
Defines validation rules for string data types. Supports regular expression patterns and common formats.

### Supported Parameters
*   `pattern` (string): Uses regular expressions to constrain the format of the string.
*   `format` (string): Validates the string against predefined common formats. Supported formats include `email`, `hostname`, `ipv4`, `ipv6`, and `uuid`.

### Unsupported Parameters
*   `minLength`
*   `maxLength`

### Request Body Example
```json
{
    "type": "object",
    "properties": {
        "user_email": {
            "type": "string",
            "description": "The user's email address",
            "format": "email"
        },
        "zip_code": {
            "type": "string",
            "description": "Six digit postal code",
            "pattern": "^\\d{6}$"
        }
    }
}
```
```

--------------------------------

### List Models - CURL Request

Source: https://api-docs.deepseek.com/api/list-models

This snippet demonstrates how to list available Deepseek API models using a CURL command. It requires an API token for authentication and specifies the Accept header for JSON responses.

```curl
curl -L -X GET 'https://api.deepseek.com/models' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer <TOKEN>'
```

--------------------------------

### Anthropic API Compatibility Details

Source: https://api-docs.deepseek.com/guides/anthropic_api

This section outlines the compatibility of DeepSeek's Anthropic API with standard Anthropic API fields, including headers, simple fields, tool fields, and message fields.

```APIDOC
## Anthropic API Compatibility Details

### HTTP Header Support

| Field          | Support Status |
|----------------|----------------|
| `anthropic-beta` | Ignored        |
| `anthropic-version`| Ignored        |
| `x-api-key`    | Fully Supported|

### Simple Field Support

| Field          | Support Status           |
|----------------|--------------------------|
| `model`        | Use DeepSeek Model Instead|
| `max_tokens`   | Fully Supported          |
| `container`    | Ignored                  |
| `mcp_servers`  | Ignored                  |
| `metadata`     | Ignored                  |
| `service_tier` | Ignored                  |
| `stop_sequences`| Fully Supported          |
| `stream`       | Fully Supported          |
| `system`       | Fully Supported          |
| `temperature`  | Fully Supported (range [0.0 ~ 2.0])|
| `thinking`     | Supported (`budget_tokens` is ignored) |
| `top_k`        | Ignored                  |
| `top_p`        | Fully Supported          |

### Tool Field Support

#### `tools`

| Field           | Support Status |
|-----------------|----------------|
| `name`          | Fully Supported|
| `input_schema`  | Fully Supported|
| `description`   | Fully Supported|
| `cache_control` | Ignored        |

#### `tool_choice`

| Value | Support Status |
|-------|----------------|
| `none`  | Fully Supported|
| `auto`  | Supported (`disable_parallel_tool_use` is ignored) |
| `any`   | Supported (`disable_parallel_tool_use` is ignored) |
| `tool`  | Supported (`disable_parallel_tool_use` is ignored) |

### Message Field Support

| Field             | Variant          | Sub-Field       | Support Status |
|-------------------|------------------|-----------------|----------------|
| `content`         | string           |                 | Fully Supported|
|                   | array, type="text" |                 | Fully Supported|
|                   |                  | `cache_control` | Ignored        |
|                   |                  | `citations`      | Ignored        |
|                   | array, type="image"|                 | Not Supported  |
|                   | array, type = "document"|                 | Not Supported  |
|                   | array, type = "search_result"|                 | Not Supported  |
|                   | array, type = "thinking"|                 | Supported      |
|                   | array, type="redacted_thinking"|                 | Not Supported  |
|                   | array, type = "tool_use"| `id`            | Fully Supported|
|                   |                  | `input`         | Fully Supported|
|                   |                  | `name`          | Fully Supported|
|                   |                  | `cache_control` | Ignored        |
|                   | array, type = "tool_result"| `tool_use_id`   | Fully Supported|
|                   |                  | `content`       | Fully Supported|
|                   |                  | `cache_control` | Ignored        |
|                   |                  | `is_error`      | Ignored        |
|                   | array, type = "server_tool_use"|                 | Not Supported  |
|                   | array, type = "web_search_tool_result"|                 | Not Supported  |
|                   | array, type = "code_execution_tool_result"|                 | Not Supported  |
|                   | array, type = "mcp_tool_use"|                 | Not Supported  |
|                   | array, type = "mcp_tool_result"|                 | Not Supported  |
|                   | array, type = "container_upload"|                 | Not Supported  |
```

--------------------------------

### Rate Limit Information

Source: https://api-docs.deepseek.com/quick_start/rate_limit

DeepSeek API does not enforce strict rate limits. Instead, it aims to serve all requests, but may experience delays during periods of high traffic. This section outlines how non-streaming and streaming requests are handled under such conditions and the maximum request duration.

```APIDOC
## Rate Limit Information

### Description
DeepSeek API does **NOT** constrain user's rate limit. We will try our best to serve every request. However, please note that when our servers are under high traffic pressure, your requests may take some time to receive a response from the server.

### Handling High Traffic
During periods of high traffic, the API handles requests as follows:

*   **Non-streaming requests**: Continuously return empty lines.
*   **Streaming requests**: Continuously return SSE keep-alive comments (`: keep-alive`).

These contents do not affect the parsing of the JSON body by the OpenAI SDK. If you are parsing the HTTP responses yourself, please ensure to handle these empty lines or comments appropriately.

### Request Timeout
If a request is still not completed after 30 minutes, the server will close the connection.
```

--------------------------------

### String Validation with Format and Pattern

Source: https://api-docs.deepseek.com/guides/tool_calls

Validates string data using predefined formats like email, hostname, IPv4, IPv6, and UUID, or custom regular expression patterns. Unsupported parameters include minLength and maxLength.

```json
{
    "type": "object",
    "properties": {
        "user_email": {
            "type": "string",
            "description": "The user's email address",
            "format": "email"
        },
        "zip_code": {
            "type": "string",
            "description": "Six digit postal code",
            "pattern": "^\\d{6}$"
        }
    }
}
```

--------------------------------

### Append Assistant Message to History (Python)

Source: https://api-docs.deepseek.com/guides/thinking_mode

This snippet demonstrates how to append a complete assistant message, including content, reasoning_content, and tool_calls, to the conversation history. It ensures all necessary fields are preserved for continued reasoning. This is useful for maintaining context between turns in a dialogue.

```python
messages.append(response.choices[0].message)

```

```python
messages.append({
    'role': 'assistant',
    'content': response.choices[0].message.content,
    'reasoning_content': response.choices[0].message.reasoning_content,
    'tool_calls': response.choices[0].message.tool_calls,
})

```

--------------------------------

### V3.1-Terminus Comparison Testing API

Source: https://api-docs.deepseek.com/guides/comparison_testing

This section details how to access the V3.1-Terminus model by modifying the base URL. It is intended for comparative testing against the V3.2-Exp model.

```APIDOC
## Accessing V3.1-Terminus

### Description
Users can access the DeepSeek-V3.1-Terminus model by changing their API `base_url`. This model is retained for experimental comparative testing and will be available until October 15, 2025.

### Method
N/A (Configuration change)

### Endpoint
`https://api.deepseek.com/v3.1_terminus_expires_on_20251015`

### Parameters
#### Query Parameters
None

#### Request Body
None

### Request Example
N/A

### Response
N/A

## Model Version Mapping

### Description
This table shows the correspondence between `base_url` settings and the specific model versions accessed.

### Method
N/A

### Endpoint
N/A

### Parameters
#### Query Parameters
None

#### Request Body
None

### Request Example
| API Type  | base_url Setting                                                     | Model Version        |
|-----------|----------------------------------------------------------------------|----------------------|
| OpenAI    | `https://api.deepseek.com`                                           | DeepSeek-V3.2-Exp    |
| Anthropic | `https://api.deepseek.com/anthropic`                                 | DeepSeek-V3.2-Exp    |
| OpenAI    | `https://api.deepseek.com/v3.1_terminus_expires_on_20251015`           | DeepSeek-V3.1-Terminus |
| Anthropic | `https://api.deepseek.com/v3.1_terminus_expires_on_20251015/anthropic` | DeepSeek-V3.1-Terminus |

### Response
N/A

## V3.1-Terminus OpenAI-Compatible API Usage Example

### Description
This section provides examples of how to invoke the API to access the V3.1-Terminus model using an OpenAI-compatible interface via curl, Python, and Node.js.

### Method
POST

### Endpoint
`https://api.deepseek.com/v3.1_terminus_expires_on_20251015/chat/completions`

### Parameters
#### Path Parameters
None

#### Query Parameters
None

#### Request Body
- **model** (string) - Required - The model to use (e.g., "deepseek-chat").
- **messages** (array) - Required - An array of message objects, each with a `role` (system, user, assistant) and `content`.
- **stream** (boolean) - Optional - Whether to stream the response.

### Request Example
```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant.", "role": "system"},
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}
```

### Response
#### Success Response (200)
- **model** (string) - The model name returned in the response (e.g., "deepseek-v3.1-terminus").
- **choices** (array) - An array of choice objects, each containing the assistant's message and finish reason.

#### Response Example
```json
{
    "model": "deepseek-v3.1-terminus",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?"
            },
            "logprobs": null,
            "finish_reason": "stop"
        }
    ]
}
```

## V3.1-Terminus Anthropic API Usage Example

### Description
This section explains how to configure the `ANTHROPIC_BASE_URL` environment variable to access the DeepSeek-V3.1-Terminus model when using an Anthropic Claude Code environment.

### Method
N/A (Environment variable configuration)

### Endpoint
`https://api.deepseek.com/v3.1_terminus_expires_on_20251015/anthropic`

### Parameters
#### Environment Variable
- **ANTHROPIC_BASE_URL** (string) - Required - Set this to `https://api.deepseek.com/v3.1_terminus_expires_on_20251015/anthropic` to access V3.1-Terminus.

### Request Example
```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/v3.1_terminus_expires_on_20251015/anthropic
```

### Response
N/A
```

--------------------------------

### Enum for Predefined String Options

Source: https://api-docs.deepseek.com/guides/tool_calls

Enforces that a string value must be one of a specific set of predefined options. This is useful for fields with a limited number of valid states, such as order status.

```json
{
    "type": "object",
    "properties": {
        "order_status": {
            "type": "string",
            "description": "Ordering status",
            "enum": ["pending", "processing", "shipped", "cancelled"]
        }
    }
}
```

--------------------------------

### Chat Completion Response Schema (JSON)

Source: https://api-docs.deepseek.com/api/create-chat-completion

This JSON object represents a full chat completion response from the Deepseek API. It includes details about the message, usage statistics, and model information. The 'bytes' field within 'logprobs' can be null if no byte representation is available for a token.

```json
{
  "id": "string",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "message": {
        "content": "string",
        "reasoning_content": "string",
        "tool_calls": [
          {
            "id": "string",
            "type": "function",
            "function": {
              "name": "string",
              "arguments": "string"
            }
          }
        ],
        "role": "assistant"
      },
      "logprobs": {
        "content": [
          {
            "token": "string",
            "logprob": 0,
            "bytes": [
              0
            ],
            "top_logprobs": [
              {
                "token": "string",
                "logprob": 0,
                "bytes": [
                  0
                ]
              }
            ]
          }
        ],
        "reasoning_content": [
          {
            "token": "string",
            "logprob": 0,
            "bytes": [
              0
            ],
            "top_logprobs": [
              {
                "token": "string",
                "logprob": 0,
                "bytes": [
                  0
                ]
              }
            ]
          }
        ]
      }
    }
  ],
  "created": 0,
  "model": "string",
  "system_fingerprint": "string",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 0,
    "prompt_tokens": 0,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 0,
    "total_tokens": 0,
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```

--------------------------------

### Number/Integer Schema

Source: https://api-docs.deepseek.com/guides/tool_calls

Specifies validation rules for numeric data types (integers and floating-point numbers). Allows setting ranges, default values, and divisibility constraints.

```APIDOC
## Number/Integer Schema

### Description
Defines validation rules for numeric data types, including integers and floating-point numbers.

### Supported Parameters
*   `const` (number): Specifies a constant numeric value.
*   `default` (number): Defines the default value of the number.
*   `minimum` (number): Specifies the minimum allowed value.
*   `maximum` (number): Specifies the maximum allowed value.
*   `exclusiveMinimum` (number): Defines a value that the number must be strictly greater than.
*   `exclusiveMaximum` (number): Defines a value that the number must be strictly less than.
*   `multipleOf` (number): Ensures that the number is a multiple of the specified value.

### Request Body Example
```json
{
    "type": "object",
    "properties": {
        "score": {
            "type": "integer",
            "description": "A number from 1-5, which represents your rating, the higher, the better",
            "minimum": 1,
            "maximum": 5
        }
    },
    "required": ["score"],
    "additionalProperties": false
}
```
```

--------------------------------

### Array Schema

Source: https://api-docs.deepseek.com/guides/tool_calls

Defines the structure and constraints for array data types. Specifies the type of items within the array.

```APIDOC
## Array Schema

### Description
Defines the structure and constraints for array data types.

### Unsupported Parameters
*   `minItems`
*   `maxItems`

### Request Body Example
```json
{
    "type": "object",
    "properties": {
        "keywords": {
            "type": "array",
            "description": "Five keywords of the article, sorted by importance",
            "items": {
                "type": "string",
                "description": "A concise and accurate keyword or phrase."
            }
        }
    },
    "required": ["keywords"],
    "additionalProperties": false
}
```
```

--------------------------------

### Chat Completion Chunk Response

Source: https://api-docs.deepseek.com/api/create-chat-completion

Details the structure of a single chunk in a streaming chat completion response. This includes information about the model, creation timestamp, completion choices, and the reason for stopping generation.

```APIDOC
## Chat Completion Chunk Response

### Description
This endpoint returns streaming chunks of chat completions. Each chunk contains partial completion data, including token information, log probabilities, and metadata about the generation process.

### Method
POST

### Endpoint
`/chat/completions

### Parameters
#### Query Parameters
None

#### Request Body
(Not detailed in the provided text, assumed to be a standard chat completion request)

### Request Example
(Not detailed in the provided text)

### Response
#### Success Response (200 OK - Chunk Stream)
- **id** (string) - Unique identifier for the chat completion.
- **choices** (array) - A list of completion choices. Each choice contains:
  - **index** (integer) - The index of the choice.
  - **delta** (object) - The change in the assistant's message.
    - **content** (string, nullable) - The text content of the message. Can be an empty string if no new content is added in this chunk.
    - **role** (string) - The role of the message (e.g., 'assistant').
  - **finish_reason** (string, nullable) - The reason the model stopped generating tokens. Possible values: `stop`, `length`, `content_filter`, `tool_calls`, `insufficient_system_resource`.
  - **logprobs** (object, nullable) - Log probabilities for the top tokens. (Details for `logprobs` and its nested fields like `token`, `logprob`, and `bytes` are provided below).
- **created** (integer) - The Unix timestamp (in seconds) of when the chat completion was created.
- **model** (string) - The model used for the completion.
- **system_fingerprint** (string) - Fingerprint representing the backend configuration.
- **object** (string) - The object type, always `chat.completion.chunk`.

#### Nested Object: `logprobs` Details
- **top_logprobs** (array) - List of the most likely tokens and their log probability at this token position.
  - Each element in the array is an object with:
    - **token** (string) - The token.
    - **logprob** (number) - The log probability of this token. `-9999.0` if unlikely.
    - **bytes** (integer[], nullable) - UTF-8 bytes representation of the token. `null` if not available.

#### Response Example (Streaming Chunk)
```json
data: {"choices": [{"delta": {"content": " Hello", "role": "assistant"}, "finish_reason": null, "index": 0, "logprobs": null}], "created": 1718345013, "id": "1f633d8bfc032625086f14113c411638", "model": "deepseek-chat", "object": "chat.completion.chunk", "system_fingerprint": "fp_a49d71b8a1"}


```

--------------------------------

### Chat Completion Chunk Schema (Streaming JSON)

Source: https://api-docs.deepseek.com/api/create-chat-completion

This schema defines the structure of a 'chat completion chunk' object, used for streaming responses from the Deepseek API. It contains delta information for message content, role, and optional log probabilities.

```json
{
  "id": "string",
  "choices": [
    {
      "delta": {
        "content": "string",
        "reasoning_content": "string",
        "role": "assistant"
      },
      "logprobs": {
        "content": [
          {
            "token": "string",
            "logprob": 0,
            "bytes": [
              0
            ],
            "top_logprobs": [
              {
                "token": "string",
                "logprob": 0,
                "bytes": [
                  0
                ]
              }
            ]
          }
        ]
      }
    }
  ]
}
```

--------------------------------

### Checking Cache Hit Status in Response

Source: https://api-docs.deepseek.com/guides/kv_cache

Details on how to identify cache hit status in the API response, specifically within the 'usage' section, highlighting the relevant token counts.

```APIDOC
## Checking Cache Hit Status

### Description
The DeepSeek API response includes specific fields within the `usage` section to indicate the effectiveness of context caching for a given request.

### Response Fields
In the `usage` section of the API response, you will find the following fields related to cache status:

1.  **prompt_cache_hit_tokens** (number): Represents the number of tokens in the input prompt of the current request that were successfully retrieved from the cache. This indicates a cache hit.
    *   Cost: 0.1 yuan per million tokens.

2.  **prompt_cache_miss_tokens** (number): Represents the number of tokens in the input prompt of the current request that were not found in the cache and therefore required full processing. This indicates a cache miss.
    *   Cost: 1 yuan per million tokens.

### Interpretation
By examining these two fields, you can quantify the extent to which context caching was utilized for your request and understand the associated cost savings or implications.
```

--------------------------------

### Deepseek API Text Completion Response Schema

Source: https://api-docs.deepseek.com/api/create-completion

The JSON schema for a successful text completion response from the Deepseek API. It includes fields for completion ID, choices, creation timestamp, model details, system fingerprint, object type, and detailed usage statistics.

```json
{
  "id": "string",
  "choices": [
    {
      "finish_reason": "stop",
      "index": 0,
      "logprobs": {
        "text_offset": [
          0
        ],
        "token_logprobs": [
          0
        ],
        "tokens": [
          "string"
        ],
        "top_logprobs": [
          {}
        ]
      },
      "text": "string"
    }
  ],
  "created": 0,
  "model": "string",
  "system_fingerprint": "string",
  "object": "text_completion",
  "usage": {
    "completion_tokens": 0,
    "prompt_tokens": 0,
    "prompt_cache_hit_tokens": 0,
    "prompt_cache_miss_tokens": 0,
    "total_tokens": 0,
    "completion_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```

--------------------------------

### Clear Reasoning Content Utility (Python)

Source: https://api-docs.deepseek.com/zh-cn/guides/thinking_mode

A utility function to clear the `reasoning_content` attribute from a list of messages. This is useful for cleaning up message history before further processing or display.

```python
def clear_reasoning_content(messages):
    for message in messages:
        if hasattr(message, 'reasoning_content'):
            message.reasoning_content = None
```

--------------------------------

### Enum Schema

Source: https://api-docs.deepseek.com/guides/tool_calls

Ensures that a field's value must be one of a predefined set of options, useful for categorical data like status codes.

```APIDOC
## Enum Schema

### Description
The `enum` keyword ensures that the output is one of the predefined options. This is useful for fields with a limited set of possible values.

### Request Body Example
```json
{
    "type": "object",
    "properties": {
        "order_status": {
            "type": "string",
            "description": "Ordering status",
            "enum": ["pending", "processing", "shipped", "cancelled"]
        }
    }
}
```
```

--------------------------------

### Checking Cache Hit Status in API Response

Source: https://api-docs.deepseek.com/guides/kv_cache

Details the fields added to the DeepSeek API response's `usage` section for monitoring context caching effectiveness. These fields quantify the cached and uncached tokens for each request.

```json
{
  "usage": {
    "prompt_cache_hit_tokens": "number",
    "prompt_cache_miss_tokens": "number"
  }
}

```

--------------------------------

### Send Chat Completion Request with cURL

Source: https://api-docs.deepseek.com/zh-cn/api/create-chat-completion

This snippet demonstrates how to send a chat completion request to the Deepseek API using cURL. It includes setting headers for authentication and content type, and provides a sample JSON payload for the request.

```curl
curl -L -X POST 'https://api.deepseek.com/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer <TOKEN>' \
--data-raw '{
  "messages": [
    {
      "content": "You are a helpful assistant",
      "role": "system"
    },
    {
      "content": "Hi",
      "role": "user"
    }
  ],
  "model": "deepseek-chat",
  "thinking": {
    "type": "disabled"
  },
  "frequency_penalty": 0,
  "max_tokens": 4096,
  "presence_penalty": 0,
  "response_format": {
    "type": "text"
  },
  "stop": null,
  "stream": false,
  "stream_options": null,
  "temperature": 1,
  "top_p": 1,
  "tools": null,
  "tool_choice": "none",
  "logprobs": false,
  "top_logprobs": null
}'
```

=== COMPLETE CONTENT === This response contains all available snippets from this library. No additional content exists. Do not make further requests.