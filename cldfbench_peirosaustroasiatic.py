import pathlib
from clldutils.misc import slug
from pylexibank import Concept, Language
from pylexibank.forms import FormSpec
from pylexibank.util import progressbar as pb
from pylexibank import Dataset as BaseDataset
import attr
import re

@attr.s
class CustomConcept(Concept):
    note = attr.ib(default=None)
    similarity = attr.ib(default=None)

@attr.s
class CustomLanguage(Language):
    Doculect = attr.ib(default=None)

class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "peirosaustroasiatic"
    concept_class = CustomConcept
    language_class = CustomLanguage

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.

        >>> args.writer.objects['LanguageTable'].append(...)
        """
        # add sources
        args.writer.add_sources()

        # add concepts
        concepts = args.writer.add_concepts(
            id_factory = lambda c:'_'.join([c.id, slug(c.gloss)]),
            lookup_factory='Name'
        )
        
        # add languages
        languages = args.writer.add_languages(
            id_factory = lambda c:slug(c['ID']),
            lookup_factory='Doculect'
        ) 

        # read in data
        data = self.raw_dir.read_csv('Peiros2004-data.txt', delimiter='\t', dicts=True)
        for gloss, entry in pb(list(enumerate(data)), desc='cldfify', total=len(data)):
            gloss = re.sub("'", "", entry['Gloss'])
            if gloss in concepts.keys():
                args.writer.add_forms_from_value(
                    Language_ID = languages[entry['Doculect'].rstrip()],
                    Parameter_ID = concepts[gloss],
                    Value = entry['Value'],
                    Source = ['Peiros2004'])
