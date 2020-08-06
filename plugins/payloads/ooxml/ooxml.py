import glob
import json
from lib.plugins.plugin import Plugin
import os
from plugins.payloads.xxe.xxe import XXE
import subprocess
from tempfile import NamedTemporaryFile


class OOXML(Plugin):
    description = "OOXML XXE Payloads built by whitel1st's docem"
    path = './third_party/docem/'

    def build(self):
        print("Generating OOXML XXE payloads with docem")
        # Generate XXE payloads for docem
        xxe = XXE(config=self.config)
        mole_payloads = xxe.build()
        docem_payloads = list()
        for i in range(0, len(mole_payloads)):
            docem_payloads.append({'vector': mole_payloads[i], 'reference': '&mole_xxe_%s' % i})

        xxe_payload_file = NamedTemporaryFile(prefix='mole_xxe', delete=False)
        with open(xxe_payload_file.name, 'w') as fout:
            for i in range(0, len(docem_payloads)):
                fout.write(json.dumps(docem_payloads[i]) + '\n')

        # Run docem
        if self.config.debug:
            stdout = subprocess.STDOUT
        else:
            stdout = open(os.devnull, 'w')
        subprocess.call('%s/docem.py -s %s/samples/xxe/sample_oxml_xxe_mod1.docx -pm xxe -pf '
                        '%s -pt per_file -b' % (self.path, self.path, xxe_payload_file.name),
                        shell=True, stdout=stdout)

        os.remove(xxe_payload_file.name)

        # Copy generated files to output dir
        word_docs = glob.glob('third_party/docem/tmp/*.docx')
        num_docs = 0
        for d in word_docs:
            if 'docx' in d:
                new_path = os.path.join(self.config.output, os.path.basename(d))
                os.rename(d, new_path)
                num_docs += 1
        print("Wrote %i documents to %s" % (num_docs, self.config.output))

        # Generate XSS payloads for docem

        # Run docem to build docs with XSS payloads

        # Copy XSS docs to output dir

        # TODO: read in files to pass back for burp generator
        return []


def setup(servers, payloads):
    payloads['ooxml'] = OOXML
