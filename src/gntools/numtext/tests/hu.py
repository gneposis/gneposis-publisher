import unittest
import gntools.numtext.hu

class KnownValuesPositive(unittest.TestCase):
    known_values = ( (1,                        'egy'),
                     (2,                        'kettő'),
                     (3,                        'három'),
                     (4,                        'négy'),
                     (5,                        'öt'),
                     (6,                        'hat'),
                     (7,                        'hét'),
                     (8,                        'nyolc'),
                     (9,                        'kilenc'),
                     (10,                       'tíz'),
                     (11,                       'tizenegy'),
                     (12,                       'tizenkettő'),
                     (13,                       'tizenhárom'),
                     (20,                       'húsz'),
                     (21,                       'huszonegy'),
                     (24,                       'huszonnégy'),
                     (25,                       'huszonöt'),
                     (30,                       'harminc'),
                     (36,                       'harminchat'),
                     (37,                       'harminchét'),
                     (40,                       'negyven'),
                     (48,                       'negyvennyolc'),
                     (49,                       'negyvenkilenc'),
                     (50,                       'ötven'),
                     (60,                       'hatvan'),
                     (70,                       'hetven'),
                     (80,                       'nyolcvan'),
                     (90,                       'kilencven'),
                     (100,                      'száz'),
                     (200,                      'kétszáz'),
                     (300,                      'háromszáz'),
                     (896,                      'nyolcszázkilencvenhat'),
                     (1000,                     'ezer'),
                     (1199,                     'ezeregyszázkilencvenkilenc'),
                     (1772,                     'ezerhétszázhetvenkettő'),
                     (2000,                     'kétezer'),
                     (2001,                     'kétezer-egy'),
                     (3016,                     'háromezer-tizenhat'),
                     (47563,                    'negyvenhétezer-ötszázhatvanhárom'),
                     (1001000,                  'egymillió-ezer'),
                     (1525000,                  'egymillió-ötszázhuszonötezer'),
                     (7490530,                  'hétmillió-négyszázkilencvenezer-ötszázharminc'),
                     (34001231,                 'harmincnégymillió-ezerkétszázharmincegy'),
                     (956432786146,             'kilencszázötvenhatmilliárd-négyszázharminckétmillió-hétszáznyolcvanhatezer-száznegyvenhat'),
                     (146321523676514,          'száznegyvenhatbillió-háromszázhuszonegymilliárd-ötszázhuszonhárommillió-hatszázhetvenhatezer-ötszáztizennégy'),
                     (999999999991999,          'kilencszázkilencvenkilencbillió-kilencszázkilencvenkilencmilliárd-kilencszázkilencvenkilencmillió-kilencszázkilencvenegyezer-kilencszázkilencvenkilenc'),
                     (999999999999999,          'kilencszázkilencvenkilencbillió-kilencszázkilencvenkilencmilliárd-kilencszázkilencvenkilencmillió-kilencszázkilencvenkilencezer-kilencszázkilencvenkilenc') )

    def test_to_text_known_values_positive(self):
        '''to_text should give known result with known positive integer input'''
        for integer, text in self.known_values:
            result = gntools.numtext.hu.to_text(integer)
            self.assertEqual(text, result)
    
    def test_from_text_known_values_positive(self):
        '''from_text should give known result with known positive text input'''
        for integer, text in self.known_values:
            result = gntools.numtext.hu.from_text(text)
            self.assertEqual(integer, result)

class ToTextZeroInput(unittest.TestCase):
    def test_to_text_zero_input(self):
        '''to_text should result "nulla" for zero input'''
        self.assertEqual(gntools.numtext.hu.to_text(0), 'nulla')

class KnownValuesNegative(unittest.TestCase):
    known_values = ( (-1,                        'mínusz egy'),
                     (-2,                        'mínusz kettő'),
                     (-3,                        'mínusz három'),
                     (-9,                        'mínusz kilenc'),
                     (-10,                       'mínusz tíz'),
                     (-11,                       'mínusz tizenegy'),
                     (-25,                       'mínusz huszonöt'),
                     (-49,                       'mínusz negyvenkilenc'),
                     (-80,                       'mínusz nyolcvan'),
                     (-100,                      'mínusz száz'),
                     (-300,                      'mínusz háromszáz'),
                     (-896,                      'mínusz nyolcszázkilencvenhat'),
                     (-1000,                     'mínusz ezer'),
                     (-1772,                     'mínusz ezerhétszázhetvenkettő'),
                     (-2000,                     'mínusz kétezer'),
                     (-2001,                     'mínusz kétezer-egy'),
                     (-47563,                    'mínusz negyvenhétezer-ötszázhatvanhárom'),
                     (-1525000,                  'mínusz egymillió-ötszázhuszonötezer'),
                     (-956432786146,             'mínusz kilencszázötvenhatmilliárd-négyszázharminckétmillió-hétszáznyolcvanhatezer-száznegyvenhat'),
                     (-999999999999999,          'mínusz kilencszázkilencvenkilencbillió-kilencszázkilencvenkilencmilliárd-kilencszázkilencvenkilencmillió-kilencszázkilencvenkilencezer-kilencszázkilencvenkilenc') )

    def test_to_text_known_values_negative(self):
        '''to_text should give known result with known negative input'''
        for integer, text in self.known_values:
            result = gntools.numtext.hu.to_text(integer)
            self.assertEqual(text, result)

    def test_from_text_known_values_negative(self):
        '''from_text should give known result with known negative text input'''
        for integer, text in self.known_values:
            result = gntools.numtext.hu.from_text(text)
            self.assertEqual(integer, result)

class ToTextBadInput(unittest.TestCase):
    def test_to_text_out_of_range_input(self):
        '''to_text should fail with input which is out of range'''
        self.assertRaises(gntools.numtext.hu.OutOfRangeError, gntools.numtext.hu.to_text, 1000000000000000)
        self.assertRaises(gntools.numtext.hu.OutOfRangeError, gntools.numtext.hu.to_text, -1000000000000000)

class FromTextBadInput(unittest.TestCase):
    known_bad_inputs = ('egymillió-egyezer', 'egyezer', 'ezer-ötszázhúsz', 'tízöt', 'ötszáznégyszáz')
    def test_from_text_out_of_range_input(self):
        '''from_text should fail with input which is known bad'''
        for s in self.known_bad_inputs:
            print(s)
            self.assertRaises(gntools.numtext.hu.InvalidInputStringError, gntools.numtext.hu.from_text, s)

class RoundtripCheck(unittest.TestCase):
    def test_roundtrip(self):
        '''from_roman(to_roman(n))==n for all n'''
        for integer in range(-3500, 3501):
            text = gntools.numtext.hu.to_text(integer)
            result = gntools.numtext.hu.from_text(text)
            self.assertEqual(integer, result)
            
        for integer in range(995000, 1005000):
            text = gntools.numtext.hu.to_text(integer)
            result = gntools.numtext.hu.from_text(text)
            self.assertEqual(integer, result)

if __name__ == "__main__":
    unittest.main()