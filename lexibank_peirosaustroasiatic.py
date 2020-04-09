from pathlib import Path
import re
import attr
from pylexibank import Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import progressbar, FormSpec, Lexeme
from clldutils.misc import slug

@attr.s
class CustomLexeme(Lexeme):
    LoanSource = attr.ib(default=None)

@attr.s
class CustomLanguage(Language):
    SubGroup = attr.ib(default=None)
    Family = attr.ib(default="Austro-Asiatic")

class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "peirosaustroasiatic"
    language_class = CustomLanguage
    lexeme_class = CustomLexeme
    form_spec = FormSpec(
        separators=("/", ","),
        strip_inside_brackets=True,
        brackets={"[": "]", "(": ")", "<": ">"},
    )

    def cmd_makecldf(self, args):
        # add sources
        args.writer.add_sources()
        # add concepts
        concepts = args.writer.add_concepts(
            id_factory=lambda c: c.id.split("-")[-1] + "_" + slug(c.english),
            lookup_factory="Name",
        )
        # fix concept
        concepts["fat (n.)"] = concepts["fat n."]
        concepts["burn (tr.)"] = concepts["burn tr."]
        concepts["to fly"] = concepts["fly v."]
        concepts["lie (down)"] = concepts["lie"]
        concepts["walk (go)"] = concepts["walk(go)"]
        args.log.info("added concepts")
        # add languages
        languages = {}
        for language in self.languages:
            args.writer.add_language(**language)
            languages[language["Name"]] = language["ID"]
        args.log.info("added languages")
        # add data
        for row_ in progressbar(
            self.raw_dir.read_csv("Peiros2004-data by etymology.txt", delimiter="\t")
        ):
            if "".join(row_).strip():
                row = dict(
                    zip(["CONCEPT", "SUBGROUP", "LANGUAGE", "FORM", "COGNACY"], row_)
                )
                bsource = ""
                if row["COGNACY"].isdigit():
                    cogid = int(row["COGNACY"])
                elif row["COGNACY"].startswith("<"):
                    bsource = row["COGNACY"].split(" ")[1]
                    cogid = 0
                else:
                    cogid = 0

                for lexeme in args.writer.add_forms_from_value(
                    Parameter_ID=concepts[re.sub("'", "", row["CONCEPT"])],
                    Language_ID=languages[row["LANGUAGE"].strip()],
                    Value=row["FORM"].strip(),
                    Source=["Peiros2004a"],
                    LoanSource=bsource,
                    Loan=True if bsource else False,
                ):
                    args.writer.add_cognate(
                        lexeme, Cognateset_ID=cogid, Source=["Peiros2004a"],
                    )
