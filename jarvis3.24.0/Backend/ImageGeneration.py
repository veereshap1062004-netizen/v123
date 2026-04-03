import requests
from PIL import Image
import os
from time import sleep
import random

def delete_previous_images(prompt):
    """Delete previous images with the same prompt"""
    folder_path = "Backend/Data"
    prompt_clean = prompt.replace(" ", "_")
    Files = [f"{prompt_clean}{i}.jpg" for i in range(1, 5)]
    
    deleted_count = 0
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"🗑️ Deleted previous image: {image_path}")
                deleted_count += 1
        except Exception as e:
            print(f"Error deleting {image_path}: {e}")
    
    if deleted_count > 0:
        print(f"✅ Deleted {deleted_count} previous images")

def open_images(prompt):
    folder_path = "Backend/Data"
    prompt_clean = prompt.replace(" ", "_")
    Files = [f"{prompt_clean}{i}.jpg" for i in range(1, 5)]
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                print(f"🖼️ Opening image: {image_path}")
                img.show()
                sleep(1)
        except Exception as e:
            print(f"Unable to open {image_path}: {e}")

def generate_images_with_flux(prompt: str):
    """Free AI image generation using Flux"""
    print("Using Flux AI generation...")
    
    try:
        flux_url = "https://image.pollinations.ai/prompt/"
        encoded_prompt = prompt.replace(" ", "%20")
        
        images_downloaded = 0
        for i in range(4):
            try:
                image_url = f"{flux_url}{encoded_prompt}?width=512&height=512&seed={random.randint(1,1000000)}"
                response = requests.get(image_url, timeout=60)
                
                if response.status_code == 200:
                    filename = f"Backend/Data/{prompt.replace(' ', '_')}{i+1}.jpg"
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Generated Flux AI image {i+1}")
                    images_downloaded += 1
                    sleep(2)
                else:
                    print(f"Flux API returned status: {response.status_code}")
                    
            except Exception as e:
                print(f"Error with Flux image {i+1}: {e}")
                continue
                
        return images_downloaded
        
    except Exception as e:
        print(f"Flux API error: {e}")
        return 0

def GenerateImages(prompt: str):
    """Main image generation function"""
    print(f"🚀 Starting AI image generation for: '{prompt}'")
    
    delete_previous_images(prompt)
    images_created = generate_images_with_flux(prompt)
    
    if images_created > 0:
        print(f"✅ Successfully generated {images_created} AI images!")
        open_images(prompt)
    else:
        print("❌ AI generation failed")
    
    return images_created

def read_image_generation_data():
    """Read from ImageGeneration.data file"""
    try:
        file_path = "Frontend/Files/ImageGeneration.data"
        with open(file_path, "r") as f:
            data = f.read().strip()
        
        print(f"📄 Read data from file: '{data}'")
        
        if "," in data:
            parts = data.split(",")
            if len(parts) >= 2:
                prompt = parts[0].strip()
                status = parts[1].strip()
                return prompt, status
        
        return None, None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None, None

def write_image_generation_data(prompt, status):
    """Write back to ImageGeneration.data file"""
    try:
        file_path = "Frontend/Files/ImageGeneration.data"
        with open(file_path, "w") as f:
            f.write(f"{prompt},{status}")
        print(f"📝 Updated file: {prompt},{status}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def main():
    print("🤖 AI Image Generation System Started!")
    print("📁 Checking: Frontend/Files/ImageGeneration.data")
    print("💡 Format: 'your prompt,True'")
    print("⏳ Waiting for image generation request...\n")
    
    while True:
        prompt, status = read_image_generation_data()
        
        if prompt and status and status.lower() == "true":
            print(f"\n🎨 AI Image generation request detected!")
            print(f"📝 Prompt: {prompt}")
            
            images_created = GenerateImages(prompt)
            write_image_generation_data("False", "False")
            print(f"📝 ImageGeneration.data reset to: False,False")
            
            if images_created > 0:
                print(f"✅ Success! Generated {images_created} AI images")
            else:
                print("❌ Failed to generate AI images")
            
            print("\n🏁 Image generation completed. Exiting program.")
            break
        else:
            sleep(2)

if __name__ == "__main__":
    main()
    
    