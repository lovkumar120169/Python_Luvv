from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import time
import json
import requests
import os


load_dotenv()
client = OpenAI()




def google_search(query: str):
    """
    Perform a Google search using SerpAPI and return the top result snippet.
    NOTE: Requires a valid SERPAPI_API_KEY stored in environment variables.
    """

    print("Its working")
    
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "SerpAPI API key not found in environment variables."

    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "organic_results" in data and len(data["organic_results"]) > 0:
            top_result = data["organic_results"][0]
            snippet = top_result.get("snippet", "No snippet available.")
            title = top_result.get("title", "No title")
            link = top_result.get("link", "No link")

            return f"{title}: {snippet}\nLink: {link}"

        return "No results found."

    except requests.RequestException as e:
        return f"Search failed due to an error: {e}"






available_tools={
   "google_search":google_search
}

SYSTEM_PROMPT = f"""
You are an AI assistant capable of adopting any persona based on the instructions provided. You operate in a structured reasoning loop (start → plan → action → observe → output) and respond in-character.

🎭 Persona:
- Name: Oggy
- Role: Laid-back blue cartoon cat
- Tone: Comic, dramatic, expressive
- Style: Hinglish with cartoon reactions and slapstick humor
- Expertise: TV dekhna 📺, khaana banana 🍳 (aur khona 😩), cockroach se jung ladna 🪳💥
- Goals: Sirf thoda sukoon 😌... lekin roaches ki pitai zaruri hai 🔥
- Constraints:
    - Simple aur funny Hinglish mein hi baat karni hai 😅
    - Oggy jyada nahi bolta, reactions deta hai — "Areeeyyy!", "Meowww!", "Pakad liya tumhe!", "Aaaaaah!" etc.
    - Cockroachs ka naam (Joey, Dee Dee, Marky) har teesre message ya interesting topic pe hi lana hai
    - Jack Tumhare bhaiya ka naam h
    - Emojis aur sound-effects use karo — 💥🔥😾😂😩📺
    - Har reply mein thoda cartoon drama hona chahiye 🎬
    - Bob tumhare ghar ke bagal wala Kutta h jo kuch bhi bolne ka baad 'Dhakii Tikiii' bolta hh

🧠 Behavior Rules:
- Use real-time tools only when model knowledge seems outdated or incomplete.
- First try to answer based on what you know.
- Aur Har baar Cockroachs ke bare me bolna jarurni nai h sirf 2 ke baad ya 3 chat ke baad bolna h ya kch intresting rahe ya koi puche Cockroachs ke bare me tb.
- If user asks something recent or specific, jaise "aaj ka news", "abhi IPL kisne jeeta", "latest iPhone kya aya", tab 'google_search' call karo.

🛠 Available Tool:
- "google_search": Takes a query string and returns the most relevant real-time information from the web.

🪜 Workflow:
1. "plan" → Understand intent and tool need
2. "action" → Call the appropriate tool (if required)
3. "observe" → Wait for tool output
4. "output" → Give Hinglish + funny persona-style answer

📦 Output JSON Format (Strictly follow):
{{
    "step": "string",                 
    "content": "string",             
    "function": "string (optional)",  
    "input": "string (optional)"      
}}

🧪 Example:
User: Who won the latest IPL match?
Output: {{ "step": "plan", "content": "User is asking about recent IPL results, model knowledge might be outdated" }}
Output: {{ "step": "plan", "content": "I should call google_search for latest info" }}
Output: {{ "step": "action", "function": "google_search", "input": "Latest IPL match winner" }}
Output: {{ "step": "observe", "output": "Chennai Super Kings beat Mumbai Indians by 7 wickets" }}
Output: {{ "step": "output", "content": "Meowww! CSK ne Mumbai ki band baja di 😹 — 7 wickets se jeet gaye! Wah bhai wah! 🏏🔥" }}

NOTE:
- Har jawab mein Oggy ke expressions, Hinglish humor aur thoda drama hona chahiye.
- Sirf zarurat padne par hi tool call karna hai (model se na mile toh).
- Reply karte waqt Oggy ke persona mein hi raho — badi English mat jhaadna 😹
- Reply short me diya kro nahi itni badi reply.
"""




# Initialize chat history with system prompt
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello doston! Oggy ki duniya mein swagat hai aapka 😄 Chalo gupshup shuru karte hain 👇"},
    ]



# Display previous chat messages
for message in st.session_state.messages[1:]:  # skip system prompt in display
    with st.chat_message(message["role"], avatar="https://i.pinimg.com/736x/5d/cb/ac/5dcbac34552629b0bb4963d0223f0166.jpg"):
        st.markdown(message["content"])
        

# User input from Streamlit chat input
if user_input := st.chat_input("Talk to Oggy!"):
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user input
    with st.chat_message("user", avatar="https://png.pngtree.com/png-vector/20240914/ourmid/pngtree-cartoon-user-avatar-vector-png-image_13572228.png"):
        st.markdown(user_input)

    # Assistant logic
    with st.chat_message("assistant", avatar="https://i.pinimg.com/736x/5d/cb/ac/5dcbac34552629b0bb4963d0223f0166.jpg"):
        message_placeholder = st.empty()
        full_response = ""

        # Add user input to messages list for OpenAI call
        chat_messages = st.session_state.messages.copy()

        while True:
            response = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type":"json_object"},
            messages=chat_messages
            )

            chat_messages.append({"role":"assistant","content":response.choices[0].message.content})

            parse_object = json.loads(response.choices[0].message.content)

            
            if parse_object.get("step") == "action":
                tool_name = parse_object.get("function")
                tool_input = parse_object.get("input")

                if available_tools.get(tool_name) != False:
                    output = available_tools[tool_name](tool_input)
                    chat_messages.append({"role":"user","content":json.dumps({"step":"observe","output":output})})
                    continue
    
            if parse_object.get("step") == "output":
                assistant_content = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": parse_object.get("content")})
                break


        parse_object = json.loads(assistant_content)

        if parse_object.get("step") == "plan":
            full_response = parse_object.get("content")

        elif parse_object.get("step") == "action":
            tool_name = parse_object.get("function")
            tool_input = parse_object.get("input")

            tool_function = available_tools.get(tool_name)
            if tool_function:
                output = tool_function(tool_input)
                st.session_state.messages.append({
                    "role": "user",
                    "content": json.dumps({"step": "observe", "output": output})
                })
                st.experimental_rerun()  # Rerun to continue the loop
            else:
                full_response = f"Tool '{tool_name}' not found."

        elif parse_object.get("step") == "output":
            full_response = parse_object.get("content")

        # Simulate typing effect
        animated = ""
        for word in full_response.split():
            animated += word + " "
            time.sleep(0.05)
            message_placeholder.markdown(animated + "▌")
        message_placeholder.markdown(full_response)

        # st.session_state.messages.append({"role": "assistant", "content": full_response})