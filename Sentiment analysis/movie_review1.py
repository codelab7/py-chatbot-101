#!/usr/bin/env python
# coding: utf-8

# In[1]:


from transformers import DistilBertConfig, DistilBertForSequenceClassification, DistilBertTokenizer
import torch

# 1. Load the tokenizer to convert text into numbers
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

# 2. Define the configuration for the model (structure/map)
config = DistilBertConfig(num_labels=2)

# 3. Load an untrained model shell based on the configuration
untrained_model = DistilBertForSequenceClassification(config)

# -------------------------------------------------------------
# 4. Take input from the user dynamically
# -------------------------------------------------------------
text = input("Please enter your sentence (in English): ")

# 5. Tokenize the input text so the model can understand it
inputs = tokenizer(text, return_tensors="pt")

# 6. Pass the inputs to the model and get the predictions
with torch.no_grad():
    outputs = untrained_model(**inputs)

# 7. Get the raw model outputs (Logits)
logits = outputs.logits

# 8. Use Softmax to convert raw logits into percentages (%)
probabilities = torch.softmax(logits, dim=1)

# ટકાવારીને અલગ વેરિયેબલમાં સેવ કરો
neg_pct = probabilities[0][0].item() * 100
pos_pct = probabilities[0][1].item() * 100

print("\n--- Result ---")
print(f"Your Input: \"{text}\"")

# -------------------------------------------------------------
# # 9. જે પરિણામ વધારે હોય, ફક્ત તે જ ડિસ્પ્લે કરો (if-else કન્ડિશન)
#-------------------------------------------------------------
if pos_pct > neg_pct:
    print(f"Prediction : Positive ({pos_pct:.2f}%)")
else:
    print(f"Prediction : Negative ({neg_pct:.2f}%)")


# In[3]:


from transformers import (
    DistilBertConfig,
    DistilBertForSequenceClassification,
    DistilBertTokenizer,
    Trainer,
    TrainingArguments
)
from datasets import load_dataset
import torch

# 1. Load the tokenizer
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

# 2. Load the IMDB dataset from Hugging Face
print("--- Downloading dataset... ---")
dataset = load_dataset("stanfordnlp/imdb")

# 3. Tokenization function (max_length=256 ensures longer sentences are not cut off)
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=256)

# Increase dataset size to 10,000 to train the model properly from scratch
print("--- Filtering data... ---")
train_dataset = dataset["train"].shuffle(seed=42).select(range(10000))

print("--- Processing (Tokenizing) data... ---")
tokenized_train = train_dataset.map(tokenize_function, batched=True)

# 4. Prepare a completely raw, untrained model (No pre-trained weights)
config = DistilBertConfig(num_labels=2)
untrained_model = DistilBertForSequenceClassification(config)

# 5. Define training hyperparameters (num_train_epochs=5 for better convergence)
training_args = TrainingArguments(
    output_dir="./results",          # Directory where model checkpoints will be saved
    learning_rate=2e-5,              # Learning rate for optimization
    per_device_train_batch_size=8,   # Batch size for training
    num_train_epochs=5,              # Number of full passes through the training data
    weight_decay=0.01,               # Regularization to prevent overfitting
    logging_dir="./logs",            # Directory for storing logs
    logging_steps=50                 # Show updates after every 50 steps
)

# 6. Initialize the Trainer (Training only, evaluation is skipped)
trainer = Trainer(
    model=untrained_model,
    args=training_args,
    train_dataset=tokenized_train,
)

# 7. Start the training process
print("\n🚀 Training from scratch started... (This may take some time)")
trainer.train()
print("🎉 Training completed successfully!")

# 8. Save the newly trained model to local storage
trainer.save_model("./my_trained_model")
tokenizer.save_pretrained("./my_trained_model")
print("💾 New custom model saved successfully in the './my_trained_model' folder.")


# In[11]:


import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

# 1. Load your saved custom model and tokenizer
model_path = "./my_trained_model"
print("--- Loading your custom trained model... ---")
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

# Make sure the model is in evaluation mode
model.eval()

print("🎉 Model loaded successfully!")
print("==================================================")


# 2. Infinite loop to take user input continuously
while True:
    # Take text input from the user
    user_text = input("👉 Enter movie review: ")

    # Check if the user wants to exit
    if user_text.lower() == 'exit':
        print("Goodbye! Exiting the program.")
        break

    # Skip empty inputs
    if not user_text.strip():
        print("Please enter some text!\n")
        continue

    # 3. Process the input text (Tokenization)
    inputs = tokenizer(user_text, return_tensors="pt", padding=True, truncation=True, max_length=256)

    # 4. Get prediction from the model
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

        # Get the highest score index (0 or 1)
        prediction = torch.argmax(logits, dim=-1).item()

        # Calculate confidence percentage (Optional but looks professional)
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence = probabilities[0][prediction].item() * 100

    # 5. Display the final result based on the prediction index
    print("-" * 40)
    if prediction == 1:
        print(f"Result: ✨ POSITIVE ✨ (Confidence: {confidence:.2f}%)")
    else:
        print(f"Result: 🔴 NEGATIVE 🔴 (Confidence: {confidence:.2f}%)")
    print("-" * 40 + "\n")


# In[9]:


from datasets import load_dataset

# 1. Load the IMDB dataset
print("--- Loading IMDB Dataset... ---")
dataset = load_dataset("stanfordnlp/imdb")

# 2. Shuffle the dataset (આનાથી પોઝિટિવ અને નેગેટિવ ડેટા મિક્સ થઈ જશે)
# seed=42 રાખવાથી દર વખતે સરખો જ મિક્સ થયેલો ડેટા મળશે
shuffled_train = dataset["train"].shuffle(seed=42)



# 3. Print the first 5 mixed samples
for i in range(10):
    review_text = shuffled_train[i]["text"]
    review_label = shuffled_train[i]["label"]

    # Convert numeric label to human-readable form (0 = Negative, 1 = Positive)
    sentiment = "✨ POSITIVE ✨" if review_label == 1 else "🔴 NEGATIVE 🔴"

    print(f"\n🎬 Mixed Movie Review #{i+1}:")
    print(f"📄 Text (First 250 chars): {review_text[:250]}...") 
    print(f"🎯 Sentiment Tag: {sentiment} (Label ID: {review_label})")
    print("-" * 60)


# In[ ]:




