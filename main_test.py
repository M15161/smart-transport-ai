from services.intent_detector import IntentDetector
from services.entity_extractor import EntityExtractor

detector = IntentDetector()

extractor = EntityExtractor()

text = input("User: ")

intent = detector.detect(text)

entities = extractor.extract(text)

print("Intent:")
print(intent)

print()

print("Entities:")
print(entities)