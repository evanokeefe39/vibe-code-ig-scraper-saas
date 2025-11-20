https://www.youtube.com/@aiDotEngineer
https://www.youtube.com/@sabrina_ramonov
https://www.youtube.com/@iamseankochel
https://www.youtube.com/@go9x
https://www.youtube.com/@trychroma
https://www.youtube.com/@ColeMedin



### Final Minimal Database Schema

- **tip_id**  
  Type: UUID (primary key)  
  Required: Yes  
  Example: `tp-7e8f9a0b-1c2d3e4f`

- **source_platform**  
  Type: String  
  Required: Yes  
  Example: `YouTube` | `TikTok` | `Instagram` | `Twitter/X` | `LinkedIn` | `Reddit`

- **post_url**  
  Type: String (URL)  
  Required: Yes  
  Example: `https://www.youtube.com/watch?v=xyz789`

- **post_date**  
  Type: Date (YYYY-MM-DD)  
  Required: Yes  
  Example: `2025-11-05`

- **domain**  
  Type: Array[String]  
  Required: Yes (multiple allowed)  
  Example: `["Performance", "Deployment", "Cost Optimization"]`  
  Suggested values: Security, Architecture, RAG, Prompt Engineering, Business, Data, Fine-tuning, Scaling, Legal/Ethics, etc.

- **original_transcript**  
  Type: Text (long)  
  Required: Yes  
  Description: Full raw transcript or caption text – this is the only source your LLM reads  
  Example: "Today I’m showing you how I cut my inference bill by 90% using vLLM..."

- **pro_tip**  
  Type: Array[String]  
  Required: Yes  
  Description: 1–5 clean, actionable pro tips extracted by the LLM (one sentence each)  
  Example:  
  `["Use vLLM with continuous batching for 4–8× higher throughput on the same GPU", "Combine Groq for demo speed and self-hosted vLLM for production", "Always enable PagedAttention to avoid OOM on long contexts"]`

- **mentioned_tools** (optional)  
  Type: Array[String]  
  Description: Only significant tools/services mentioned (LLM decides relevance)  
  Example: `["vLLM", "Groq", "RunPod", "Together.ai", "Axolotl", "Unsloth", "Fireworks", "LangChain"]`

- **mentioned_models** (optional)  
  Type: Array[String]  
  Description: Only significant model mentions (include size when possible)  
  Example: `["Llama-3.1-70B", "Mixtral-8x22B", "Claude-3.5-Sonnet", "GPT-4o", "Gemma-2-27B"]`

- **llm_processed_at** (optional)  
  Type: DateTime  
  Example: `2025-11-18 10:21:33`

EXAMPLE RECORD:

{
  "tip_id": "tp-a1b2c3d4",
  "source_platform": "TikTok",
  "post_url": "https://www.tiktok.com/@aihustler/video/743210987654321",
  "post_date": "2025-10-28",
  "domain": ["Security", "Cost Optimization"],
  "original_transcript": "I got drained $12k in one night because I left my OpenAI key in the frontend bundle...",
  "pro_tip": [
    "Never expose API keys in client-side code — always proxy through your own backend",
    "Use environment variables + a /api/chat endpoint instead of calling OpenAI directly from the browser",
    "Set up daily spend alerts and hard limits in the OpenAI dashboard"
  ],
  "mentioned_tools": ["OpenAI", "Vercel", "Next.js"],
  "mentioned_models": ["GPT-4o"],
  "llm_processed_at": "2025-11-18 14:32:11"
}