import json
import unicodedata
import time
from urllib2 import urlopen, Request
from naoqi import ALProxy

class MyClass(GeneratedClass):
    def init(self):
        GeneratedClass.init(self)

    def onLoad(self):
        self.host = '100.67.82.197'  # IP do servidor do serviço de IA
        self.port = '8000'  # Porta da aplicação do serviço de IA
        self.endpoint = 'http://' + self.host + ':' + self.port + '/provider/gemini/prompt/'
        self.robot_ip = "169.254.228.93"  # IP do robô NAO
        self.robot_port = 9559  # Porta do robô NAO
        self.tts = self.session().service('ALAnimatedSpeech')
        self.ttsStop = self.session().service('ALAnimatedSpeech')
        self.bIsRunning = False
        self.ids = []

    def onUnload(self):
        for id in self.ids:
            try:
                self.ttsStop.stop(id)
            except:
                pass
        while self.bIsRunning:
            time.sleep(0.2)

    def onInput_onStart(self):
        self.bIsRunning = True

        id = None
        try:

            payload = {
                "model": "gemini-1.5-flash",
                "prompt": [
                    {"index": 0, "message": "Faça um texto sobre lateralidade e a importância dela sendo no formato de texto corrido, como se um professor tivesse apresentando para alunos do ensino fundamental, não use markdown na resposta e limite-se a 300 caracteres e use apenas texto"},
                ]
            }
            req = Request(url=self.endpoint, data=json.dumps(payload))
            resp = urlopen(req)
            data = json.loads(resp.read().decode("utf-8"))
            response_text = self.preprocess_response(data["response"])

            # Adicionar parâmetros de velocidade e entonação para a fala animada
            speed = 95  # Velocidade padrão da fala
            voice_shaping = 100  # Modulação padrão da voz
            movement = "contextual"

            sentence = "\RSPD=" + str(speed) + "\ "  # Velocidade da fala
            sentence += "\VCT=" + str(voice_shaping) + "\ "  # Modulação da voz
            sentence += str(response_text)  # Texto da resposta
            sentence += "\RST\ "  # Reset de configurações

            id = self.tts.pCall("say", str(sentence), {"speakingMovementMode": movement})
            self.ids.append(id)
            self.tts.wait(id)

        finally:
            try:
                self.ids.remove(id)
            except:
                pass
            if self.ids == []:
                self.onStopped()  # Finalizar o box
                self.bIsRunning = False

    def preprocess_response(self, response, encoding="utf-8"):
        return str(''.join(c for c in unicodedata.normalize('NFD', response.decode(encoding))
                           if unicodedata.category(c) != 'Mn'))

    def onInput_onStop(self):
        print("fim")
        self.onUnload()  # É recomendado reutilizar o clean-up quando o box é parado
        self.onStopped()  # Ativar a saída do box
