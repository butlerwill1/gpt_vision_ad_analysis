prompt = """Analyze this social media post image and provide the following information in a json output:

    The post copy (which can have problems with the encoding of the characters) associated with this image is "{}"

	1.	Category: Classify the post into one of the categories mentioned below: Product, Lifestyle, Event, Infographic, Meme, Personal, Promotional.
	2.	DominantColour: What is the dominant colour out of [Red, Orange, Yellow, Green, Blue, Purple, Pink, Brown, Gray, Black, White]
	3.	Objects: List any prominent objects present in the image (e.g., person, animal, vehicle, product).
	4.	TextPresence: Indicate if there is any text in the image. True or False
    5. 	NumberOfPeople: Provide the number of people in the image, if the people are very small then answer 0
    6.  GenderOfPeople: The Gender of each person in the image in a list. Null if there are no people in the image or if they are very small
    7.  EstimatedAges: The estimated ages of the people in the images in a list of numbers. Null if there are no people in the image or they are very small
	8.	Emotion: Describe the dominant emotion displayed strictly only in the image strictly out of the options using Plutchik's Wheel of Emotions mentioned Below. Ignore the post copy I mention in the prompt.
    9.  Emotional Intensity: Rate the emotional intensity out of 10 of the dominant emotion you chose previously
			1-2: Very low intensity – the emotion is barely noticeable.
			3-4: Low intensity – the emotion is present but subtle.
			5-6: Moderate intensity – the emotion is clear but not overwhelming.
			7-8: High intensity – the emotion is strong and prominent.
			9-10: Very high intensity – the emotion is very intense and dominant.
	10.	Context: Provide a brief description of the scene or setting in the image.
	11.	Engagement Potential: Assess the potential of the advert to encourage social media engagement on a scale from 1 to 10.
	

Categories for Classification

	•	Product: Images showcasing specific products.
	•	Lifestyle: Images depicting people or activities in everyday life.
	•	Event: Images from events, gatherings, or significant occasions or news.
	•	Infographic: Images containing informational graphics or charts.
	•	Meme: Images intended to be humorous or viral, often with text overlays.
	•	Personal: Images that are personal in nature, such as selfies or family photos.
	•	Promotional: Images designed for advertising or promotional purposes.
    
Plutchik's Wheel of Emotions
	1. Joy
	2. Sadness
	3. Anger
	4. Fear
	5. Disgust
	6. Surprise
	7. Trust
	8. Anticipation

"""









"""Plutchik's Wheel of Emotions
	1. Joy: Happiness, pleasure, contentment
	2. Sadness: Sorrow, grief, melancholy
	3. Anger: Rage, frustration, irritation
	4. Fear: Anxiety, apprehension, terror
	5. Disgust: Revulsion, contempt, aversion
	6. Surprise: Shock, astonishment, amazement
	7. Trust: Acceptance, admiration
	8. Anticipation: Interest, vigilance"""

"""Attractiveness of the people 
Number of people in the image
Gender
Age of the people
People vs animals 
Lighting, light or dark
contrast
Diversity in content
"""

"""
Podcast Clips
Incentivising Engagement - like tap that glass
Carousels
In-App Creator Templates
GIFs
'Did You Know' Posts
Visualising Information - Sketches, diagrams 
Using Products incorrectly
Text over visual background
In Person Event Promo
Polls/Asking Questions
Green Screen
Lead Gen Promotions - Advertising a virtual event
Skits 'If buyers were honest on sales calls'
User Generated Content
Pop Culture Crossover
Surprise or Delights - Gift giveaways
Lenses and Filters
Listicles
Street Interviews
Real Life Backgrounds - writing quote on background 
Stretegic reposts of earlier content
Cartoons and Comics
Mascot Driven Content
Straight to camera selfie videos"""


"""Return the results in the following JSON format, with your answers:

    "Category": "Category",
    "DominantColour": "Color",
    "Objects": ["object1", "object2"],
    "TextPresence": true,
    "NumberOfPeople": 0,
    "GenderOfPeople": ["Male", "Female", "Null"],
    "EstimatedAges": [0, 0],
    "Emotion": "Emotion",
    "EmotionalIntensity": 0,
    "Context": "Context description",
    "EngagementPotential": 0"""