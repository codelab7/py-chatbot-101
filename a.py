from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

# 1. FastAPI એપ્લિકેશન શરૂ કરો
app = FastAPI(
    title="HuggingFace Model API",
    description="Hugging Face મોડેલનો ઉપયોગ કરીને ટેક્સ્ટ સેન્ટિમેન્ટ ચેક કરવા માટેનું API",
    version="1.0"
)

# 2. Hugging Face પાઇપલાઇન લોડ કરો (આપણે Sentiment Analysis મોડેલ વાપરી રહ્યા છીએ)
# પહેલીવાર રન કરતી વખતે આ મોડેલ ડાઉનલોડ થશે, પછી તે લોકલ કેશમાંથી ચાલશે.
try:
    classifier = pipeline("sentiment-analysis",model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    print(f"મોડેલ લોડ કરવામાં ભૂલ આવી: {e}")
    classifier = None

# 3. યુઝર ઇનપુટ માટે Pydantic મોડેલ વ્યાખ્યાયિત કરો
class TextInput(BaseModel):
    text: str

# 4. API એન્ડપોઇન્ટ (POST Request)
@app.post("/analyze-sentiment")
async def analyze_sentiment(input_data: TextInput):
    # જો મોડેલ લોડ ન થયું હોય તો એરર આપો
    if classifier is None:
        raise HTTPException(status_code=500, detail="મોડેલ ઉપલબ્ધ નથી.")
    
    # ઇનપુટ ટેક્સ્ટ ખાલી નથી તે ચેક કરો
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="મહેરબાની કરીને યોગ્ય ટેક્સ્ટ લખો.")
    
    try:
        # મોડેલ દ્વારા પ્રિડિક્શન કરો
        predictions = classifier(input_data.text)
        
        # અહીં ચેક કરો કે આઉટપુટ લિસ્ટ છે અને તે ખાલી નથી
        if isinstance(predictions, list) and len(predictions) > 0:
            prediction = predictions[0]
        else:
            prediction = predictions

        # સેફ્ટી ચેક: જો કોઈ કારણસર હજુ પણ ડિક્શનરી ન હોય
        if not isinstance(prediction, dict):
            raise ValueError("મોડેલનું આઉટપુટ યોગ્ય ફોર્મેટમાં નથી.")
        
        # ક્લીન JSON રિસ્પોન્સ રિટર્ન કરો
        return {
            "status": "success",
            "input_text": input_data.text,
            "result": {
                "label": prediction.get("label"),  # ડાયરેક્ટ બ્રેકેટના બદલે .get() વાપરવું વધુ સેફ છે
                "confidence_score": round(prediction.get("score", 0), 4)
            }
        }
    except Exception as e:
        # અહીં str(e) ની જગ્યાએ પૂરી વિગત પ્રિન્ટ થશે જેથી ટર્મિનલમાં સાચી ખબર પડે
        print(f"Error details: {e}") 
        raise HTTPException(status_code=500, detail=f"પ્રોસેસિંગમાં ભૂલ આવી: {str(e)}")

# 5. હેલ્થ ચેક એન્ડપોઇન્ટ
@app.get("/")
def home():
    return {"message": "HuggingFace FastAPI App ઇઝ રનિંગ!"}