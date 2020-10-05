#!/usr/bin/python
#
# Copyright 2015 Johannes Grassler <johannes@btw23.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# mdtableconv.py - converts pipe tables to Pandoc's grid tables
import markdown.extensions.admonition as adm
import markdown.blockparser
import re

class AdmonitionFilter(adm.AdmonitionProcessor):

    RE = re.compile(r'(?:^|\n)(?:!!!|\?\?\?)\ ?([\w\-]+)(?:\ "?([^"\n]+)"?)?')

    def __init__(self, encoding='utf-8', tab_length = 4):
        self.encoding = encoding
        self.tab_length = tab_length

    def blocks(self, lines):
        """Groups lines into markdown blocks"""
        state = markdown.blockparser.State()
        blocks = []

        # We use three states: start, ``` and '\n'
        state.set('start')

        # index of current block
        currblock = -1

        for line in lines:
            new_block = False
            if state.isstate('start'):
                if line.startswith('!!!') or line.startswith('???'):
                    state.set('!!!')
                new_block = True
            elif state.isstate('!!!'):
                if line.startswith('!!!') or line.startswith('???'):
                    new_block = True
                elif line.strip() != '' and not line.startswith('    '):
                    state.set('start')
                    new_block = True
                else:
                    line += '\n'

            if new_block:
                blocks.append('')
                currblock += 1

            blocks[currblock] += line

        return blocks

    def run(self, lines):
        """Filter method: Passes all blocks through convert_admonition() and returns a list of lines."""
        ret = []

        blocks = self.blocks(lines)
        for block in blocks:
            ret.extend(self.convert_admonition(block))

        return ret

    def convert_admonition(self, block):
        lines = block.split('\n')
        if self.RE.search(block):
            lines = block.strip().split('\n')
            m = self.RE.search(lines.pop(0))
            klass, title = self.get_class_and_title(m)
            lines = list(map(lambda x:self.detab(x)[0], lines))
            lines = ['\n'.join(lines)]
            lines.insert(0, f'### {klass.title()}: {title}\n')
            lines.append('\n')

        return lines
