import unittest
import pkg_resources as pr
import os

from matext.fetch_fields import _get_forlagsbeskrivelse, _get_provider_id, _get_lektor


def read_file(path):
    with open(path) as fh:
        return fh.read()


class TestParseCommonData(unittest.TestCase):

    def setUp(self):

        testfiles_path = pr.resource_filename('matext', 'tests/data')
        self.forlag_9788711378434 = read_file(os.path.join(testfiles_path, '150015-forlag:9788711378434-commonData.xml'))
        self.basis_27825680 = read_file(os.path.join(testfiles_path, '870970-basis:27825680.xml'))
        self.allanmeld_31487048 = read_file(os.path.join(testfiles_path, '870976-allanmeld:31487048.xml'))

    def test_get_forlagsbeskrivelse(self):

        pid, text = _get_forlagsbeskrivelse(self.forlag_9788711378434)

        expected = '''En amerikansk forfatter på bryllupsrejse i Sydfrankrig forsøger at genoptage forfatterskabet, men modarbejdes hemmeligt af sin kone, der med vilje inddrager ham i et trekantforhold til en anden kvinde.<br><br>I Edens have fra 1886 foregribes en senere kønsdebat, og bogen hører til blandt dem, der gør at den udbredte opfattelse af Hemingways mandschauvinistiske kvindesyn må revurderes. I fortællingen viser Hemingway ikke blot interesse for androgyne karakterer, han eksperimenterer også med de for tiden traditionelle rollefordelinger. <br>'''

        self.assertEqual(text, expected)

        expected_pid = '870970-basis:50728471'
        self.assertEqual(expected_pid, pid)

    def test_publizon_provider_id(self):

        pid, data = _get_provider_id(self.basis_27825680)
        expected = '9788711437223'
        self.assertEqual(expected, data)
        
    def test_lektor(self):

        pid, data = _get_lektor(self.allanmeld_31487048)
        expected = {'Kort om bogen': 'Letlæst bog om utroskab fra serien "Læseværkstedet". Bogen egner sig til unge og voksne med læsevanskeligheder, til brug i undervisningen og som fritidslæsning', 'Beskrivelse': 'Mikkel og Mette er gift og har to børn. De har travlt på deres arbejde. Mette er lærer og underviser i mange timer. Mikkel er fotograf og elsker at tage gode billeder af sine kunder. Historien starter i dagene op til jul. Mikkel begynder pludselig at komme sent hjem fra arbejde. Mette er vred. Hun vil have, at han hjælper med at hente børnene. Mikkel lyver og siger, han har travlt. Men hvad er der galt? Og hvem køber Mikkel smykker til? Historien bliver fortalt på skift af Mette og Mikkel. På forsiden er der et billede af en pose slik, som indgår i historien. "Utro" er en del af serien "Læseværkstedet" i grønt niveau, lix 13. Alle bøger i serien er også udgivet som lydbøger', 'Vurdering': 'Bogen er nem at læse med et relevant emne. Det er interessant at høre både Mettes og Mikkels side af historien, og det kan fx åbne op for en god diskussion i undervisningen. Ligesom den åbne slutning kan gøre det', 'Andre bøger om samme emne': 'Kirsten Ahlburg har skrevet flere bøger om den svære kærlighed for læsesvage unge og voksne i samme letlæsnings-serie. Fx i Et lille håb', 'Til bibliotekaren': 'Utroskab er et emne, som mange kan forholde sig til. Anbefales til indkøb. Special-pædagogisk forlag udgiver en lang række bøger til læsesvage unge og voksne i serien "Læseværkstedet" på 5 niveauer'}

        self.assertEqual(expected, data)
