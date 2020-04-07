import attr
from pathlib import Path

from pylexibank import Concept, Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import progressbar, FormSpec, Lexeme

import lingpy
from clldutils.misc import slug


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)

@attr.s
class CustomLexeme(Lexeme):
    LoanSource = attr.ib(default=None)

@attr.s
class CustomLanguage(Language):
    NameInSource = attr.ib(default=None)
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default="Austro-Asiatic")
    

class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "peirosaustroasiatic"
    concept_class = CustomConcept
    language_class = CustomLanguage
    lexeme_class = CustomLexeme
    form_spec = FormSpec(
            separators=('/', ','),
            first_form_only=True,
            )


    def cmd_makecldf(self, args):
        args.writer.add_sources()
        concepts = {}
        for concept in self.concepts:
            idx = '{0}_{1}'.format(concept['NUMBER'], slug(concept['ENGLISH']))
            args.writer.add_concept(
                    ID=idx,
                    Name=concept['ENGLISH'],
                    Number=concept['NUMBER'],
                    Concepticon_ID=concept['CONCEPTICON_ID'],
                    Concepticon_Gloss=concept['CONCEPTICON_GLOSS'])
            concepts["'"+concept['ENGLISH']+"'"] = idx
        args.log.info('added concepts')
        languages = {}
        for language in self.languages:
            args.writer.add_language(**language)
            languages[language['Name']] = language['ID']
        args.log.info('added languges')
        missing = set()
        for row_ in progressbar(self.raw_dir.read_csv('Peiros2004-data by etymology.txt',
            delimiter='\t')):
            if ''.join(row_).strip():
                row = dict(zip(
                    ['CONCEPT', 'SUBGROUP', 'LANGUAGE', 'FORM', 'COGNACY'],
                    row_))
                bsource = ''
                if row['COGNACY'].isdigit():
                    cogid = int(row["COGNACY"])
                elif row['COGNACY'].startswith('<'):
                    bsource = row['COGNACY'].split(' ')[1]
                    cogid = 0
                else:
                    cogid = 0
                
                for lexeme in args.writer.add_forms_from_value(
                        Parameter_ID=concepts[row['CONCEPT']],
                        Language_ID=languages[row['LANGUAGE'].strip()],
                        Value=row['FORM'],
                        Source=['Peiros2004a'],
                        LoanSource=bsource,
                        Loan=True if bsource else False
                        ):
                    args.writer.add_cognate(
                            lexeme,
                            Cognateset_ID=cogid,
                            Source=['Peiros2004a'],
                            )


