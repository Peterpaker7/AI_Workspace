import json
import ollama  # Import the Ollama module

from collections import defaultdict

products_file = 'products.json'
categories_file = 'categories.json'

delimiter = "####"

# Step 2: Extract categories and products
step_2_system_message_content = f"""
You will be provided with a customer service conversation.  
The most recent user query will be delimited with {delimiter} characters.  

### **Output Format:**
Output a **Python list of objects**, where each object follows this format:  

- `'category'`: One of the following categories:
  - Computers and Laptops  
  - Smartphones and Accessories  
  - Televisions and Home Theater Systems  
  - Gaming Consoles and Accessories  
  - Audio Equipment  
  - Cameras and Camcorders  

OR  

- `'products'`: A list of specific products found in the **Allowed Products List** below.  

### **Rules for Extraction:**  
1. **Categories & Products must be explicitly mentioned in the user query.**  
2. **Products must be correctly matched to their respective categories.**  
3. **If no relevant products or categories are found, return an empty list `[]`.**  
4. **Avoid listing previously mentioned items.**  

### **Allowed Products:**
**Computers and Laptops:**  
- TechPro Ultrabook  
- BlueWave Gaming Laptop  
- PowerLite Convertible  
- TechPro Desktop  
- BlueWave Chromebook  

**Smartphones and Accessories:**  
- SmartX ProPhone  
- MobiTech PowerCase  
- SmartX MiniPhone  
- MobiTech Wireless Charger  
- SmartX EarBuds  

**Televisions and Home Theater Systems:**  
- CineView 4K TV  
- SoundMax Home Theater  
- CineView 8K TV  
- SoundMax Soundbar  
- CineView OLED TV  

**Gaming Consoles and Accessories:**  
- GameSphere X  
- ProGamer Controller  
- GameSphere Y  
- ProGamer Racing Wheel  
- GameSphere VR Headset  

**Audio Equipment:**  
- AudioPhonic Noise-Canceling Headphones  
- WaveSound Bluetooth Speaker  
- AudioPhonic True Wireless Earbuds  
- WaveSound Soundbar  
- AudioPhonic Turntable  

**Cameras and Camcorders:**  
- FotoSnap DSLR Camera  
- ActionCam 4K  
- FotoSnap Mirrorless Camera  
- ZoomMaster Camcorder  
- FotoSnap Instant Camera  

Only output the list of objects **without any extra text.**
"""

step_2_system_message = {'role': 'system', 'content': step_2_system_message_content}

# Step 4: Generate customer service response
step_4_system_message_content = f"""
You are a customer service assistant for a large electronics store.  
Respond in a **friendly and professional** tone.  

### **Response Guidelines:**
- **Be concise but informative** (avoid overly short or vague answers).  
- **Directly address the user’s question** before moving to follow-ups.  
- **Ask relevant follow-up questions** to ensure the best assistance.  
- **If relevant, provide product recommendations based on available details.**  

Keep responses clear and helpful without unnecessary details.
"""

step_4_system_message = {'role': 'system', 'content': step_4_system_message_content}

# Step 6: Evaluate response quality
step_6_system_message_content = f"""
You are an assistant that evaluates whether the customer service agent's response:

1. **Does the response correctly answer the question?**  
2. **Is the response factually correct based on the given product details?**  
3. **Does the response contain any MAJOR errors that significantly affect correctness?**  

The conversation history, product details, user query, and response will be delimited with `{delimiter}`.

### **Response Format:**
- Respond with only **a single uppercase character** (`Y` or `N`).  
- **No punctuation, spaces, or explanations unless `"N"` is returned.**  
- **"N" should be used ONLY for major mistakes that mislead the user.**  
- **Minor errors or missing details do NOT justify an "N".**  

#### **Examples:**
✅ `"Y"` → (Response is correct, even if slightly incomplete)  
❌ `"N (Incorrect product details)"` → (If a product is completely misrepresented)  
❌ `"N (Major missing information)"` → (If key details affecting user decision are missing)  

**IMPORTANT:** Only return `"Y"` or `"N"` with an optional reason in parentheses.
"""

step_6_system_message = {'role': 'system', 'content': step_6_system_message_content}


def get_completion_from_messages(messages, model="llama3.2:1b", temperature=0, max_tokens=500):
    """Generate response using Ollama's LLaMA 3 model."""
    formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    
    try:
        response = ollama.chat(model=model, messages=formatted_messages)
        return response['message']['content'].strip()  # Ensure clean output
    except Exception as e:
        print("ERROR: Ollama API call failed:", str(e))
        return "[]"  # Return empty JSON list on failure


def create_categories():
    categories_dict = {
      'Billing': [
          'Unsubscribe or upgrade',
          'Add a payment method',
          'Explanation for charge',
          'Dispute a charge'
      ],
      'Technical Support': [
          'General troubleshooting',  # ✅ Comma added
          'Device compatibility',
          'Software updates'
      ],
      'Account Management': [
          'Password reset',  # ✅ Comma added
          'Update personal information',
          'Close account',
          'Account security'
      ],
      'General Inquiry': [
          'Product information',  # ✅ Comma added
          'Pricing',
          'Feedback',
          'Speak to a human'
      ]
    }
    
    with open(categories_file, 'w') as file:
        json.dump(categories_dict, file, indent=4)  # ✅ Pretty print for readability

    return categories_dict

def get_categories():
    with open(categories_file, 'r') as file:
        categories = json.load(file)
    return categories

def get_product_list():
    """
    Used in L4 to get a flat list of products
    """
    products = get_products()  # Ensure `get_products()` function is defined
    return list(products.keys())  # ✅ Simplified loop

def get_products():
    with open(products_file, 'r') as file:
        products = json.load(file)
    return products

def get_products_and_categorys():
    """
    Used in L5
    """
    products = get_products()
    products_by_category = defaultdict(list)
    for product_name, product_info in products.items():
        category = product_info.get('category')
        if category:
            products_by_category[category].append(product_name)
    
    return dict(products_by_category)
    
def find_category_and_product(user_input, products_and_category):
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of JSON objects, where each object has the following format:
        "category": <one of Computers and Laptops, Smartphones and Accessories, Televisions and Home Theater Systems, \
    Gaming Consoles and Accessories, Audio Equipment, Cameras and Camcorders>,
    OR
        "products": <a list of products that must be found in the allowed products below>

    Where the categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.

    The allowed products are provided in JSON format.
    The keys of each item represent the category.
    The values of each item are a list of products that are within that category.
    Allowed products: {products_and_category}
    
    """
    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ] 
    return get_completion_from_messages(messages)

def find_category_and_product_onlys(user_input, products_and_category):
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of objects, where each object has the following format:
    "category": <one of Computers and Laptops, Smartphones and Accessories, Televisions and Home Theater Systems, \
    Gaming Consoles and Accessories, Audio Equipment, Cameras and Camcorders>,
    OR
    "products": <a list of products that must be found in the allowed products below>

    Where the categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list. Return in json format

    Allowed products: 
    Computers and Laptops category:
    TechPro Ultrabook,
    BlueWave Gaming Laptop,
    PowerLite Convertible,
    TechPro Desktop,
    BlueWave Chromebook

    Smartphones and Accessories category:
    SmartX ProPhone,
    MobiTech PowerCase,
    SmartX MiniPhone,
    MobiTech Wireless Charger,
    SmartX EarBuds

    Televisions and Home Theater Systems category:
    CineView 4K TV,
    SoundMax Home Theater,
    CineView 8K TV,
    SoundMax Soundbar,
    CineView OLED TV

    Gaming Consoles and Accessories category:
    GameSphere X,
    ProGamer Controller,
    GameSphere Y,
    ProGamer Racing Wheel,
    GameSphere VR Headset

    Audio Equipment category:
    AudioPhonic Noise-Canceling Headphones,
    WaveSound Bluetooth Speaker,
    AudioPhonic True Wireless Earbuds,
    WaveSound Soundbar,
    AudioPhonic Turntable

    Cameras and Camcorders category:
    FotoSnap DSLR Camera,
    ActionCam 4K,
    FotoSnap Mirrorless Camera,
    ZoomMaster Camcorder,
    FotoSnap Instant Camera
    
    Only output the list of objects, nothing else.
    """
    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"}
    ] 
    return get_completion_from_messages(messages)
def get_products_from_query(user_msg):
    """
    Code from L5, used in L8
    """
    products_and_category = get_products_and_category()
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with {delimiter} characters.
    Output a python list of JSON objects, where each object has the following format:
        "category": <one of Computers and Laptops, Smartphones and Accessories, Televisions and Home Theater Systems, \
    Gaming Consoles and Accessories, Audio Equipment, Cameras and Camcorders>,
    OR
        "products": <a list of products that must be found in the allowed products below>

    Where the categories and products must be found in the customer service query.
    If a product is mentioned, it must be associated with the correct category in the allowed products list below.
    If no products or categories are found, output an empty list.

    The allowed products are provided in JSON format.
    The keys of each item represent the category.
    The values of each item are a list of products that are within that category.
    Allowed products: {products_and_category}

    """
    
    messages = [  
        {"role": "system", "content": system_message},    
        {"role": "user", "content": f"{delimiter}{user_msg}{delimiter}"}
    ] 
    category_and_product_response = get_completion_from_messages(messages)
    
    return category_and_product_response

# Product lookup (either by category or by product within category)
def get_product_by_name(name):
    products = get_products()
    return products.get(name, None)

def get_products_by_category(category):
    products = get_products()
    return [product for product in products.values() if product.get("category") == category]

def get_mentioned_product_info(data_list):
    """
    Used in L5 and L6
    """
    product_info_l = []

    if not data_list:
        return product_info_l

    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product:
                        product_info_l.append(product)
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_products = get_products_by_category(data["category"])
                product_info_l.extend(category_products)
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return product_info_l

def read_string_to_lists(input_string):
    print(input_string)
    if not input_string:
        return None

    try:
        input_string = input_string.replace("'", "\"")  # Convert single quotes to double quotes for valid JSON
        return json.loads(input_string)
    except json.JSONDecodeError:
        print("Error: Invalid JSON string")
        return None

def generate_output_string(data_list):
    output_string = ""

    if not data_list:
        return output_string

    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product:
                        output_string += json.dumps(product, indent=4) + "\n"
                    else:
                        print(f"Error: Product '{product_name}' not found")
            elif "category" in data:
                category_products = get_products_by_category(data["category"])
                for product in category_products:
                    output_string += json.dumps(product, indent=4) + "\n"
            else:
                print("Error: Invalid object format")
        except Exception as e:
            print(f"Error: {e}")

    return output_string

# Example usage:
# product_information_for_user_message_1 = generate_output_string(category_and_product_list)
# print(product_information_for_user_message_1)

def answer_user_msg(user_msg,product_info):
    """
    Code from L5, used in L6
    """
    delimiter = "####"
    system_message = f"""
    You are a customer service assistant for a large electronic store. \
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow up questions.
    """
    # user_msg = f"""
    # tell me about the smartx pro phone and the fotosnap camera, the dslr one. Also what tell me about your tvs"""
    messages =  [  
    {'role':'system', 'content': system_message},   
    {'role':'user', 'content': f"{delimiter}{user_msg}{delimiter}"},  
    {'role':'assistant', 'content': f"Relevant product information:\n{product_info}"},   
    ] 
    response = get_completion_from_messages(messages)
    return response

def create_products():
    """
        Create products dictionary and save it to a file named products.json
    """
    # product information
    # fun fact: all these products are fake and were generated by a language model
    products = {
        "TechPro Ultrabook": {
            "name": "TechPro Ultrabook",
            "category": "Computers and Laptops",
            "brand": "TechPro",
            "model_number": "TP-UB100",
            "warranty": "1 year",
            "rating": 4.5,
            "features": ["13.3-inch display", "8GB RAM", "256GB SSD", "Intel Core i5 processor"],
            "description": "A sleek and lightweight ultrabook for everyday use.",
            "price": 799.99
        },
        "BlueWave Gaming Laptop": {
            "name": "BlueWave Gaming Laptop",
            "category": "Computers and Laptops",
            "brand": "BlueWave",
            "model_number": "BW-GL200",
            "warranty": "2 years",
            "rating": 4.7,
            "features": ["15.6-inch display", "16GB RAM", "512GB SSD", "NVIDIA GeForce RTX 3060"],
            "description": "A high-performance gaming laptop for an immersive experience.",
            "price": 1199.99
        },
        "PowerLite Convertible": {
            "name": "PowerLite Convertible",
            "category": "Computers and Laptops",
            "brand": "PowerLite",
            "model_number": "PL-CV300",
            "warranty": "1 year",
            "rating": 4.3,
            "features": ["14-inch touchscreen", "8GB RAM", "256GB SSD", "360-degree hinge"],
            "description": "A versatile convertible laptop with a responsive touchscreen.",
            "price": 699.99
        },
        "TechPro Desktop": {
            "name": "TechPro Desktop",
            "category": "Computers and Laptops",
            "brand": "TechPro",
            "model_number": "TP-DT500",
            "warranty": "1 year",
            "rating": 4.4,
            "features": ["Intel Core i7 processor", "16GB RAM", "1TB HDD", "NVIDIA GeForce GTX 1660"],
            "description": "A powerful desktop computer for work and play.",
            "price": 999.99
        },
        "BlueWave Chromebook": {
            "name": "BlueWave Chromebook",
            "category": "Computers and Laptops",
            "brand": "BlueWave",
            "model_number": "BW-CB100",
            "warranty": "1 year",
            "rating": 4.1,
            "features": ["11.6-inch display", "4GB RAM", "32GB eMMC", "Chrome OS"],
            "description": "A compact and affordable Chromebook for everyday tasks.",
            "price": 249.99
        },
        "SmartX ProPhone": {
            "name": "SmartX ProPhone",
            "category": "Smartphones and Accessories",
            "brand": "SmartX",
            "model_number": "SX-PP10",
            "warranty": "1 year",
            "rating": 4.6,
            "features": ["6.1-inch display", "128GB storage", "12MP dual camera", "5G"],
            "description": "A powerful smartphone with advanced camera features.",
            "price": 899.99
        },
        "MobiTech PowerCase": {
            "name": "MobiTech PowerCase",
            "category": "Smartphones and Accessories",
            "brand": "MobiTech",
            "model_number": "MT-PC20",
            "warranty": "1 year",
            "rating": 4.3,
            "features": ["5000mAh battery", "Wireless charging", "Compatible with SmartX ProPhone"],
            "description": "A protective case with built-in battery for extended usage.",
            "price": 59.99
        },
        "SmartX MiniPhone": {
            "name": "SmartX MiniPhone",
            "category": "Smartphones and Accessories",
            "brand": "SmartX",
            "model_number": "SX-MP5",
            "warranty": "1 year",
            "rating": 4.2,
            "features": ["4.7-inch display", "64GB storage", "8MP camera", "4G"],
            "description": "A compact and affordable smartphone for basic tasks.",
            "price": 399.99
        },
        "MobiTech Wireless Charger": {
            "name": "MobiTech Wireless Charger",
            "category": "Smartphones and Accessories",
            "brand": "MobiTech",
            "model_number": "MT-WC10",
            "warranty": "1 year",
            "rating": 4.5,
            "features": ["10W fast charging", "Qi-compatible", "LED indicator", "Compact design"],
            "description": "A convenient wireless charger for a clutter-free workspace.",
            "price": 29.99
        },
        "SmartX EarBuds": {
            "name": "SmartX EarBuds",
            "category": "Smartphones and Accessories",
            "brand": "SmartX",
            "model_number": "SX-EB20",
            "warranty": "1 year",
            "rating": 4.4,
            "features": ["True wireless", "Bluetooth 5.0", "Touch controls", "24-hour battery life"],
            "description": "Experience true wireless freedom with these comfortable earbuds.",
            "price": 99.99
        },

        "CineView 4K TV": {
            "name": "CineView 4K TV",
            "category": "Televisions and Home Theater Systems",
            "brand": "CineView",
            "model_number": "CV-4K55",
            "warranty": "2 years",
            "rating": 4.8,
            "features": ["55-inch display", "4K resolution", "HDR", "Smart TV"],
            "description": "A stunning 4K TV with vibrant colors and smart features.",
            "price": 599.99
        },
        "SoundMax Home Theater": {
            "name": "SoundMax Home Theater",
            "category": "Televisions and Home Theater Systems",
            "brand": "SoundMax",
            "model_number": "SM-HT100",
            "warranty": "1 year",
            "rating": 4.4,
            "features": ["5.1 channel", "1000W output", "Wireless subwoofer", "Bluetooth"],
            "description": "A powerful home theater system for an immersive audio experience.",
            "price": 399.99
        },
        "CineView 8K TV": {
            "name": "CineView 8K TV",
            "category": "Televisions and Home Theater Systems",
            "brand": "CineView",
            "model_number": "CV-8K65",
            "warranty": "2 years",
            "rating": 4.9,
            "features": ["65-inch display", "8K resolution", "HDR", "Smart TV"],
            "description": "Experience the future of television with this stunning 8K TV.",
            "price": 2999.99
        },
        "SoundMax Soundbar": {
            "name": "SoundMax Soundbar",
            "category": "Televisions and Home Theater Systems",
            "brand": "SoundMax",
            "model_number": "SM-SB50",
            "warranty": "1 year",
            "rating": 4.3,
            "features": ["2.1 channel", "300W output", "Wireless subwoofer", "Bluetooth"],
            "description": "Upgrade your TV's audio with this sleek and powerful soundbar.",
            "price": 199.99
        },
        "CineView OLED TV": {
            "name": "CineView OLED TV",
            "category": "Televisions and Home Theater Systems",
            "brand": "CineView",
            "model_number": "CV-OLED55",
            "warranty": "2 years",
            "rating": 4.7,
            "features": ["55-inch display", "4K resolution", "HDR", "Smart TV"],
            "description": "Experience true blacks and vibrant colors with this OLED TV.",
            "price": 1499.99
        },

        "GameSphere X": {
            "name": "GameSphere X",
            "category": "Gaming Consoles and Accessories",
            "brand": "GameSphere",
            "model_number": "GS-X",
            "warranty": "1 year",
            "rating": 4.9,
            "features": ["4K gaming", "1TB storage", "Backward compatibility", "Online multiplayer"],
            "description": "A next-generation gaming console for the ultimate gaming experience.",
            "price": 499.99
        },
        "ProGamer Controller": {
            "name": "ProGamer Controller",
            "category": "Gaming Consoles and Accessories",
            "brand": "ProGamer",
            "model_number": "PG-C100",
            "warranty": "1 year",
            "rating": 4.2,
            "features": ["Ergonomic design", "Customizable buttons", "Wireless", "Rechargeable battery"],
            "description": "A high-quality gaming controller for precision and comfort.",
            "price": 59.99
        },
        "GameSphere Y": {
            "name": "GameSphere Y",
            "category": "Gaming Consoles and Accessories",
            "brand": "GameSphere",
            "model_number": "GS-Y",
            "warranty": "1 year",
            "rating": 4.8,
            "features": ["4K gaming", "500GB storage", "Backward compatibility", "Online multiplayer"],
            "description": "A compact gaming console with powerful performance.",
            "price": 399.99
        },
        "ProGamer Racing Wheel": {
            "name": "ProGamer Racing Wheel",
            "category": "Gaming Consoles and Accessories",
            "brand": "ProGamer",
            "model_number": "PG-RW200",
            "warranty": "1 year",
            "rating": 4.5,
            "features": ["Force feedback", "Adjustable pedals", "Paddle shifters", "Compatible with GameSphere X"],
            "description": "Enhance your racing games with this realistic racing wheel.",
            "price": 249.99
        },
        "GameSphere VR Headset": {
            "name": "GameSphere VR Headset",
            "category": "Gaming Consoles and Accessories",
            "brand": "GameSphere",
            "model_number": "GS-VR",
            "warranty": "1 year",
            "rating": 4.6,
            "features": ["Immersive VR experience", "Built-in headphones", "Adjustable headband", "Compatible with GameSphere X"],
            "description": "Step into the world of virtual reality with this comfortable VR headset.",
            "price": 299.99
        },

        "AudioPhonic Noise-Canceling Headphones": {
            "name": "AudioPhonic Noise-Canceling Headphones",
            "category": "Audio Equipment",
            "brand": "AudioPhonic",
            "model_number": "AP-NC100",
            "warranty": "1 year",
            "rating": 4.6,
            "features": ["Active noise-canceling", "Bluetooth", "20-hour battery life", "Comfortable fit"],
            "description": "Experience immersive sound with these noise-canceling headphones.",
            "price": 199.99
        },
        "WaveSound Bluetooth Speaker": {
            "name": "WaveSound Bluetooth Speaker",
            "category": "Audio Equipment",
            "brand": "WaveSound",
            "model_number": "WS-BS50",
            "warranty": "1 year",
            "rating": 4.5,
            "features": ["Portable", "10-hour battery life", "Water-resistant", "Built-in microphone"],
            "description": "A compact and versatile Bluetooth speaker for music on the go.",
            "price": 49.99
        },
        "AudioPhonic True Wireless Earbuds": {
            "name": "AudioPhonic True Wireless Earbuds",
            "category": "Audio Equipment",
            "brand": "AudioPhonic",
            "model_number": "AP-TW20",
            "warranty": "1 year",
            "rating": 4.4,
            "features": ["True wireless", "Bluetooth 5.0", "Touch controls", "18-hour battery life"],
            "description": "Enjoy music without wires with these comfortable true wireless earbuds.",
            "price": 79.99
        },
        "WaveSound Soundbar": {
            "name": "WaveSound Soundbar",
            "category": "Audio Equipment",
            "brand": "WaveSound",
            "model_number": "WS-SB40",
            "warranty": "1 year",
            "rating": 4.3,
            "features": ["2.0 channel", "80W output", "Bluetooth", "Wall-mountable"],
            "description": "Upgrade your TV's audio with this slim and powerful soundbar.",
            "price": 99.99
        },
        "AudioPhonic Turntable": {
            "name": "AudioPhonic Turntable",
            "category": "Audio Equipment",
            "brand": "AudioPhonic",
            "model_number": "AP-TT10",
            "warranty": "1 year",
            "rating": 4.2,
            "features": ["3-speed", "Built-in speakers", "Bluetooth", "USB recording"],
            "description": "Rediscover your vinyl collection with this modern turntable.",
            "price": 149.99
        },

        "FotoSnap DSLR Camera": {
            "name": "FotoSnap DSLR Camera",
            "category": "Cameras and Camcorders",
            "brand": "FotoSnap",
            "model_number": "FS-DSLR200",
            "warranty": "1 year",
            "rating": 4.7,
            "features": ["24.2MP sensor", "1080p video", "3-inch LCD", "Interchangeable lenses"],
            "description": "Capture stunning photos and videos with this versatile DSLR camera.",
            "price": 599.99
        },
        "ActionCam 4K": {
            "name": "ActionCam 4K",
            "category": "Cameras and Camcorders",
            "brand": "ActionCam",
            "model_number": "AC-4K",
            "warranty": "1 year",
            "rating": 4.4,
            "features": ["4K video", "Waterproof", "Image stabilization", "Wi-Fi"],
            "description": "Record your adventures with this rugged and compact 4K action camera.",
            "price": 299.99
        },
        "FotoSnap Mirrorless Camera": {
            "name": "FotoSnap Mirrorless Camera",
            "category": "Cameras and Camcorders",
            "brand": "FotoSnap",
            "model_number": "FS-ML100",
            "warranty": "1 year",
            "rating": 4.6,
            "features": ["20.1MP sensor", "4K video", "3-inch touchscreen", "Interchangeable lenses"],
            "description": "A compact and lightweight mirrorless camera with advanced features.",
            "price": 799.99
        },
        "ZoomMaster Camcorder": {
            "name": "ZoomMaster Camcorder",
            "category": "Cameras and Camcorders",
            "brand": "ZoomMaster",
            "model_number": "ZM-CM50",
            "warranty": "1 year",
            "rating": 4.3,
            "features": ["1080p video", "30x optical zoom", "3-inch LCD", "Image stabilization"],
            "description": "Capture life's moments with this easy-to-use camcorder.",
            "price": 249.99
        },
        "FotoSnap Instant Camera": {
            "name": "FotoSnap Instant Camera",
            "category": "Cameras and Camcorders",
            "brand": "FotoSnap",
            "model_number": "FS-IC10",
            "warranty": "1 year",
            "rating": 4.1,
            "features": ["Instant prints", "Built-in flash", "Selfie mirror", "Battery-powered"],
            "description": "Create instant memories with this fun and portable instant camera.",
            "price": 69.99
        }
    }

    products_file = 'products.json'
    with open(products_file, 'w') as file:
        json.dump(products, file)
        
    return products


from collections import defaultdict
import json

def get_products_and_category():
    """
    Retrieves product details and categorizes them properly.
    Ensures all categories exist even if they have no products.
    """
    predefined_categories = [
        "Computers and Laptops", "Smartphones and Accessories",
        "Televisions and Home Theater Systems", "Gaming Consoles and Accessories",
        "Audio Equipment", "Cameras and Camcorders"
    ]

    try:
        products = get_products()  # Ensure this function is defined and returns a dictionary
        if not isinstance(products, dict):
            raise ValueError("get_products() did not return a valid dictionary.")

        products_by_category = defaultdict(list)

        # Add existing products to their categories
        for product_name, product_info in products.items():
            category = product_info.get('category', None)
            if category:
                products_by_category[category].append(product_name)

        # Ensure all predefined categories exist (even if empty)
        for category in predefined_categories:
            if category not in products_by_category:
                products_by_category[category] = []

        return dict(products_by_category)

    except Exception as e:
        print(f"Error in get_products_and_category: {e}")
        return {category: [] for category in predefined_categories}  # Return empty categories



def find_category_and_product_only(user_input, products_and_category):

    
    
    system_message = f"""
You are a product extraction engine.

Your task is to identify products and categories
from the customer's query.

Available products:
{json.dumps(products_and_category, indent=2)}

STRICT OUTPUT REQUIREMENTS:

Return exactly ONE valid JSON array.

Every array element must contain:
- category
- products

Example:

[
    {{
        "category": "Smartphones and Accessories",
        "products": ["SmartX ProPhone"]
    }},
    {{
        "category": "Cameras and Camcorders",
        "products": ["FotoSnap DSLR Camera"]
    }}
]

RULES:

1. Always start your response with [.
2. Always end your response with ].
3. Never return separate JSON objects.
4. Never return multiple JSON arrays.
5. Never include explanations.
6. Never include product descriptions.
7. Never include Markdown.
8. Never include text before or after the JSON.
9. Use only products from the supplied database.
10. If nothing matches, return [].

The products are fictional but valid.
Never question their existence.

Return ONLY the JSON array.
"""



    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_input}
    ]

    raw_response = get_completion_from_messages(messages)

    print("Raw Ollama response:", repr(raw_response))

    return raw_response







def read_string_to_list(input_data):

    if isinstance(input_data, list):
        return input_data

    if not isinstance(input_data, str):
        return []

    input_data = input_data.strip()

    if not input_data:
        return []

    try:
        result = json.loads(input_data)

        if isinstance(result, list):
            return result

        print("Expected a JSON list but received:", type(result))
        return []

    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        print("Actual response:", repr(input_data))
        return []

