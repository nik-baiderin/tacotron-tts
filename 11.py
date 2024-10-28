from file_handler import FileHandler
from models import models, ALL_MODELS
_valid_model_types = [key for key in models if key is not ALL_MODELS]

samples = [
    "Съешь же ещё этих мягких французских булок да выпей чаю. В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!Широкая электрификация южных губерний даст мощный толчок подъёму сельского хозяйства.",
    "Широкая электрификация южных губерний даст мощный толчок подъёму сельского хозяйства.",
    "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!"
]

response_code, results = FileHandler.get_synthesized_audio(samples[0], "Ruslan")