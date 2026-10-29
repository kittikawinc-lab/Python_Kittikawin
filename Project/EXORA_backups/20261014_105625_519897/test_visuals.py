import unittest
from PIL import Image
import EXORA_visuals as visuals

class VisualTests(unittest.TestCase):
    def test_login_split_fits_fhd(self):
        self.assertEqual(visuals.login_size(1920,1050),(1640,860))
        w,h=visuals.login_size(1280,720)
        self.assertLess(w,1280);self.assertLess(h,720)
    def test_artwork_resizes_without_network(self):
        image=visuals.hero(450,430)
        self.assertEqual(image.size,(450,430));self.assertEqual(image.mode,'RGB')
        self.assertGreater(len(image.getcolors(450*430)),20)

if __name__=='__main__':unittest.main(verbosity=2)
