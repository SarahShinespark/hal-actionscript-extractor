#!/usr/bin/python3

# Some of the code you'll see here is bad, but it works.

import argparse
import os
import string
import sys

#Takes in a PC address (exact byte length)
#Returns a SNES address in LoROM SlowROM format
#I grabbed these two formulas from a SMW page
def to_snes_addr(pc):
    return ((pc << 1) & 0x7f0000) | (pc & 0x7fff) | 0x8000

#Takes in a SNES 3-byte pointer.
#Returns it, in PC format for Python.
# This is for Paladin's Quest, so it's LoROM format and little endian.
def to_pc_addr(snes):
    return ((snes & 0x7f0000) >> 1) | (snes & 0x7fff)

warning_addresses = []


LABEL_CHARSET = string.ascii_letters + string.digits + '_'  # Valid characters for labels

LAST_SCRIPT = 134  # Amount of scripts

SCRIPT_BLOCKS = (  # Why the hell are these PC ADDRESSES AND NOT SNES ADDRESSES when the symbols and asm_funcs are using SNES format??
    (to_pc_addr(0x00CEE4), to_pc_addr(0x00CF47)),   # Loading save file
    (to_pc_addr(0x00CFCF), to_pc_addr(0x00D01C)),   # Stage select stuff
    (to_pc_addr(0x00D0A9), to_pc_addr(0x00D0CF)),   # I don't know
    (to_pc_addr(0x00D375), to_pc_addr(0x00D40E)),   # Sound test
    (to_pc_addr(0x018321), to_pc_addr(0x018A24)),   #Event 00: Game Init
    (to_pc_addr(0x018A68), to_pc_addr(0x018B75)),   #Event 01
    (to_pc_addr(0x018C85), to_pc_addr(0x019BD7)),   # Dungeon walking
    (to_pc_addr(0x019BE5), to_pc_addr(0x01A1A2)),   # Map menu
    (to_pc_addr(0x01A32F), to_pc_addr(0x01A39E)),   #Event 02
    (to_pc_addr(0x01A477), to_pc_addr(0x01A4A1)),   #Event 03
    (to_pc_addr(0x01B807), to_pc_addr(0x01B9B3)),   #Event 6A: Credits scene
    (to_pc_addr(0x01BADC), to_pc_addr(0x01BB19)),   # Credits stuff
    (to_pc_addr(0x01BB57), to_pc_addr(0x01BB64)),   # Credits stuff
    (to_pc_addr(0x01BBC8), to_pc_addr(0x01BC09)),   # Credits stuff
    (to_pc_addr(0x01BC51), to_pc_addr(0x01BC5E)),   #Event 6B: Staff Roll
    (to_pc_addr(0x028001), to_pc_addr(0x0280EE)),   #Enemy 00: Slime
    (to_pc_addr(0x03ADFE), to_pc_addr(0x03AE12)),   #Event 69: Nice
    (to_pc_addr(0x03B88B), to_pc_addr(0x03BA78)),   # Towns; Movement, Axs house etc
    (to_pc_addr(0x03BA99), to_pc_addr(0x03BB27)),   # Icorina house
    (to_pc_addr(0x03BB35), to_pc_addr(0x03CC4A)),   # Event 68: Shop Gfx; Town Shop Handling
    (to_pc_addr(0x03CDC2), to_pc_addr(0x03CFF3)),   # Field Sprites; Card Sprites
    (to_pc_addr(0x03D00A), to_pc_addr(0x03D013)),   # Sub: Loop til A or B press
    (to_pc_addr(0x058001), to_pc_addr(0x0581BE)),   #Event 04: Rooks
    (to_pc_addr(0x058312), to_pc_addr(0x0587E2)),   #Event 05: Sylph; Load Attribute/Cond. color
    (to_pc_addr(0x05884E), to_pc_addr(0x058998)),   #Event 06: Dao
    (to_pc_addr(0x0589EB), to_pc_addr(0x058B35)),   #Event 07: Marid
    (to_pc_addr(0x058B88), to_pc_addr(0x058CD2)),   #Event 08: Efrite
    (to_pc_addr(0x058D25), to_pc_addr(0x058E08)),   #Event 09: Teefa
    (to_pc_addr(0x058E19), to_pc_addr(0x058F08)),   # Teefa part 2
    (to_pc_addr(0x058F57), to_pc_addr(0x0590BB)),   #Event 0A: Salah
    (to_pc_addr(0x05910A), to_pc_addr(0x0592C9)),   #Event 0B: Darwin
    (to_pc_addr(0x059318), to_pc_addr(0x05947C)),   #Event 0C: Axs
    (to_pc_addr(0x0594CB), to_pc_addr(0x05963F)),   #Event 0D-0F: Skull card;
    (to_pc_addr(0x059650), to_pc_addr(0x059705)),   # Battle; Damage distortion, status display
    (to_pc_addr(0x059716), to_pc_addr(0x059B0D)),   # Battle; Battle menu
    (to_pc_addr(0x059B2E), to_pc_addr(0x059D4A)),   # Battle; Spells, Equipment, Cards, Defend, Run
    (to_pc_addr(0x05F137), to_pc_addr(0x05F565)),   # Using items and spells
    (to_pc_addr(0x05F5A7), to_pc_addr(0x05F5D1)),   # Animate enemy attack?
    (to_pc_addr(0x05F5DF), to_pc_addr(0x05F5F1)),   # Ruinous Mission
    (to_pc_addr(0x05F95F), to_pc_addr(0x05FA26)),   # Battle; Using Cards
    (to_pc_addr(0x0F8001), to_pc_addr(0x0F8179)),   #Event 10: Battle Animations
    (to_pc_addr(0x0FCB2B), to_pc_addr(0x0FCF30)),   #Event 11: Spell Animations
    (to_pc_addr(0x17804D), to_pc_addr(0x17811A)),   #Event 14: Opening movie
    (to_pc_addr(0x178BAF), to_pc_addr(0x178BCE)),   # Opening movie graphics loading
    (to_pc_addr(0x178BEF), to_pc_addr(0x178C6D)),   #Event 15: Intro weather; etc
    (to_pc_addr(0x18849C), to_pc_addr(0x1884E7)),   #Event 16: Treasure Chests
    (to_pc_addr(0x1884F2), to_pc_addr(0x1884FB)),   # Some orphaned treasure chest code
    (to_pc_addr(0x18968B), to_pc_addr(0x1896C9)),   #Event 12: Main Story
    (to_pc_addr(0x1896CC), to_pc_addr(0x189731)),   #STORY 00: Ch01 Rooks intro
    (to_pc_addr(0x189795), to_pc_addr(0x189840)),   #STORY 01: Ch01 Ariel/Teefa intro
    (to_pc_addr(0x189843), to_pc_addr(0x189848)),   #STORY 02: Ch01 Leaving Galia
    (to_pc_addr(0x18985D), to_pc_addr(0x189B7A)),   #STORY 03: Ch01 Crystal Sword room
    (to_pc_addr(0x189C4B), to_pc_addr(0x189D71)),   # Ch01 end parts 1, 6
    (to_pc_addr(0x189D96), to_pc_addr(0x189D84)),   # Ch01 end part 5
    (to_pc_addr(0x189DC9), to_pc_addr(0x189DF7)),   # Ch01 end part 4
    (to_pc_addr(0x189E0C), to_pc_addr(0x189E35)),   # Ch01 end parts 2, 3
    (to_pc_addr(0x18A002), to_pc_addr(0x18A130)),   #STORY 04: Ch02 Salah/Axs intro
    (to_pc_addr(0x18A189), to_pc_addr(0x18A19A)),   # Ch02 start animations (enter Salah/Axs)
    (to_pc_addr(0x18A1B7), to_pc_addr(0x18A2AF)),   #STORY 05: Ch02 Darwin intro
    (to_pc_addr(0x18A2F0), to_pc_addr(0x18A354)),   # Ch02 Darwin animations
    (to_pc_addr(0x18A369), to_pc_addr(0x18A41B)),   #STORY 06: Ch02 Darwin joins
    (to_pc_addr(0x18A430), to_pc_addr(0x18A4AE)),   #STORY 07: Ch02 Darwin leaves
    (to_pc_addr(0x18A4C3), to_pc_addr(0x18A82B)),   #STORY 08: Ch02 Reinoll visit
    (to_pc_addr(0x18AA07), to_pc_addr(0x18AA52)),   # Ch02 Reinoll animations
    (to_pc_addr(0x18D9D9), to_pc_addr(0x18D9EF))    #Event 17: Overworld
)

DATA_TYPE_SIZES = {
    'label_16': 2,  # 16-bit address (preferably a label, when available)
    'label_24': 3,  # 24-bit address (preferably a label, when available)
    'imm_8':    1,  # 8-bit immediate (hex representation)
    'imm_s8':   1,  # 8-bit signed immediate (decimal representation)
    'imm_u8':   1,  # 8-bit unsigned immediate (decimal representation)
    'imm_16':   2,  # 16-bit immediate (hex representation)
    'imm_s16':  2,  # 16-bit signed immediate (decimal representation)
    'imm_u16':  2,  # 16-bit unsigned immediate (decimal representation)
    'addr_16':  2,  # 16-bit address
    'addr_24':  3,  # 24-bit address
    'addr_32':  4,  # 32-bit address (high byte ignored)
    'obj_var':  1,  # Object variable (i.e. VAR0, VAR1, ..., VAR7)
    'reg':      0,  # The work register
    'nop':      0,  # Special, used only by opcode 0x0F (ONTICK NOP)
}

# (mnemonic, data types separated by spaces)
OPCODES = (
    ('END',         ''),                        # 00
    ('START_LOOP',  'imm_u8'),                  # 01
    ('END_LOOP',    ''),                        # 02
    ('JML',         'label_24'),                # 03
    ('JSL',         'label_24'),                # 04
    ('RTL',         ''),                        # 05
    ('WAIT',        'imm_u8'),                  # 06
    ('ASM_CALL',    'label_24'),                # 07
    ('TASK',        'label_16'),                # 08
    ('ON_TICK',     'label_24'),                # 09
    ('HALT',        ''),                        # 0A
    ('JEQ',         'label_16'),                # 0B
    ('JNE',         'label_16'),                # 0C
    ('END_TASK',    ''),                        # 0D
    ('BIN_OP.w',    'label_16 imm_u8 imm_16'),  # 0E - BINOP with 16-bit memory value
    ('MOV',         'obj_var imm_16'),          # 0F - Store 16b value in obj_var
    ('ONTICK',      'nop'),                     # 10
    ('MULTI_JMP',   'imm_u8'),                  # 11 - Jumps to a variable list of pointers
    ('MULTI_JSR',   'imm_u8'),                  # 12 - Subroutine to a variable list of pointers
    ('MOV.b',       'addr_16 imm_8'),           # 13 - Store 8b value in obj_var
    ('UNK_TASK',    'imm_s8'),                  # 14
    ('BIN_OP',      'obj_var imm_u8 imm_16'),   # 15 - BINOP with object variable
    ('MOV.w',       'label_16 imm_16'),         # 16 - Store 16bit value to memory
    ('BREAK_EQ',    'label_16'),                # 17 - JEQ and break out of loop
    ('BREAK_NE',    'label_16'),                # 18
    ('BIN_OP.b',    'label_16 imm_u8 imm_8'),   # 19 - BINOP with 8-bit memory value
    ('JMP',         'label_16'),                # 1A
    ('JSR',         'label_16'),                # 1B
    ('RTS',         ''),                        # 1C
    ('SET_ANIM_PTR','label_24'),                # 1D - Saves animation data ptr to object's $0A9F
    ('MOV',         'reg imm_16'),              # 1E - Load 16bit value
    ('MOV',         'reg label_16'),            # 1F - Load 16bit memory
    ('WEIRD_1'      'imm_8'),                   # 20 - Involves applying position/velocity changes
    ('WEIRD_2',     'imm_8'),                   # 21 - Nonexistant instruction in Earthbound
    ('WEIRD_3',     'imm_8'),                   # 22 - Nonexistant instruction in Earthbound
    ('MOV',         'obj_var reg'),             # 23 - STA obj_var [0-3]
    ('MOV',         'reg obj_var'),             # 24 - LDA obj_var [0-3]
    ('WAIT',        'obj_var'),                 # 25 - Waits [obj_var 0-3's value] frames (text speed)
    # SPECIAL INSTRUCTIONS BEGIN
    ('SET_ANIM',    'imm_s8'),                  # 30
    ('SET_XPOS',    'imm_s16'),                 # 38
    ('SET_YPOS',    'imm_s16'),                 # 40
    ('ADD_XPOS',    'imm_s16'),                 # 48
    ('ADD_YPOS',    'imm_s16'),                 # 50
    ('SET_XVEL',    'imm_s16'),                 # 58
    ('SET_YVEL',    'imm_s16'),                 # 60
    ('ADD_XVEL',    'imm_s16'),                 # 68
    ('ADD_YVEL',    'imm_s16'),                 # 70
    ('BGH_DISP',    'imm_u8 imm_16'),           # 78 - Set background horizontal displacement          (Earthbound: UNK31)
    ('BGV_DISP',    'imm_u8 imm_16'),           # 80 - Set background vertical displacement            (Earthbound: UNK32)
    ('SET_BGH_VEL', 'imm_u8 imm_16'),           # 88 - Set background horizontal displacement velocity (Earthbound: UNK33)
    ('SET_BGV_VEL', 'imm_u8 imm_16'),           # 90 - Set background vertical displacement velocity   (Earthbound: UNK34)
    ('ADD_BGH_VEL', 'imm_u8 imm_16'),           # 98 - Add background horizontal displacement velocity
    ('ADD_BGV_VEL', 'imm_u8 imm_16'),           # A0 - Add background vertical displacement velocity
    ('INC_ANIM',    ''),                        # A8
    ('DEC_ANIM',    ''),                        # B0
    ('ADD_ANIM',    'imm_s8'),                  # B8
    ('UNK_37',      'imm_8 imm_16'),            # C0 - SUM_1
    ('UNK_38',      'imm_8 imm_16'),            # C8 - SUM_2
    ('ZERO_VEL',     ''),                       # D0
    ('ZR_BG_DISPVEL','imm_8'),                  # D8 - Zero background displacement velocity (Earthbound: UNK3A)
    ('SET_ZPOS',    'imm_s16'),                 # E0
    ('ADD_ZPOS',    'imm_s16'),                 # E8
    ('SET_ZVEL',    'imm_s16'),                 # F0
    ('ADD_ZVEL',    'imm_s16'),                 # F8
)

BINOPS = ('AND', 'OR', 'ADD', 'XOR')

class Disassembler(object):
    def __init__(self, rom_file, out_file, sym_file, asm_functions_file, header_offset, script_count, indent=4):
        self._indent = indent
        self.rom_file = rom_file
        self.out_file = out_file
        self.sym_file = sym_file
        self.asm_functions_file = asm_functions_file
        self.header_offset = header_offset
        self.script_count = script_count
        self.indentation = self._indent
        self.pc = 0
        self.was_linebreak = False
        self.force_label = False
        self.symbols = dict()
        self.asm_functions = dict()
        self.init_asm_functions()
        self.init_symbols()

    @property
    def snes_pc(self):
        addr = self.pc
        bank = addr >> 15
        addr = ((addr & 0x7FFF) + ((bank & 0x3F) * 0x10000)) | 0x8000
        #Took forever to find this bug, but bank & 0x2F will display addr 18xxxx as 08xxxx

        return addr

    def read_rom(self, amount, signed=False):
        b = self.rom_file.read(amount)
        return int.from_bytes(b, signed=signed, byteorder='little')

    def datatype_to_str(self, data_type, bytes_):
        value = int.from_bytes(bytes_, byteorder='little')
        if data_type == 'label_16':
            if value < 0x8000:
                bank_mask = 0
            else:
                bank_mask = self.snes_pc & 0xFF0000
            return self.symbols.get(bank_mask | value, '${:04X}'.format(value))
        elif data_type == 'label_24':
            return self.symbols.get(value, '${:06X}'.format(value))
        elif data_type == 'imm_8':
            return '#${:02X}'.format(value)
        elif data_type == 'imm_16':
            return '#${:04X}'.format(value)
        elif data_type in ('imm_s8', 'imm_s16'):
            value = int.from_bytes(bytes_, signed=True, byteorder='little')
            return '#{}'.format(value)
        elif data_type in ('imm_u8', 'imm_u16'):
            return '#{}'.format(value)
        elif data_type == 'addr_16':
            return '${:04X}'.format(value)
        elif data_type == 'addr_24':
            return '${:06X}'.format(value)
        elif data_type == 'addr_32':
            value = ((value & 0xFFFF0000) >> 16) | ((value & 0xFFFF) << 16)  # addr_32 has a weird-ass format
            return '${:06X}'.format(value)
        elif data_type == 'obj_var':
            if value > 3:
                print('AT {:06X} -'.format(self.snes_pc), 'WARNING: INVALID OBJ_VAR OPERAND:', value)

            return 'VAR{}'.format(value)
        elif data_type in ('reg', 'nop'):
            return data_type.upper()
        else:
            raise TypeError('Unknown data type! ({})'.format(data_type))

    def try_add_label(self):
        label = self.symbols.get(self.snes_pc)

        if self.force_label:
            if not label:
                label = 'L_{:06X}'.format(self.snes_pc)
                self.symbols[self.snes_pc] = label

            label = '\n' + label

        if label:
            self.out_file.write(label + ':\n')

        return bool(label)

    def disassemble_all(self):
        self.force_label = False  # For first
        for start, end in SCRIPT_BLOCKS:
            self.rom_file.seek(start)
            self.pc = self.rom_file.tell()

            while self.pc < end:
                was_label = self.try_add_label()
                self.was_linebreak = was_label or self.was_linebreak
                self.force_label = False

                opcode = self.read_rom(1)
                self.disasm_opcode(opcode)
                self.force_label = opcode in (0x00, 0x03, 0x05, 0x0A, 0x0E, 0x1A, 0x1C)
                self.pc = self.rom_file.tell()
        #Sort the list of warnings after disassemble all
#        if warning_addresses:
#            warning_addresses.sort()
#            for x in warning_addresses:
#                print("WARNING: I DON'T KNOW ANYTHING ABOUT ASM FUNCTION {:06X}".format(x))

    def disasm_opcode(self, op_byte):
        indentation = ' ' * self.indentation

        waited = 0
        opcode = op_byte
        if opcode >= 0x30:
            waited = opcode & 0x07
            opcode = (((opcode - 0x30) & 0xF8) >> 3) + 0x26

        if opcode >= len(OPCODES):
            to_write = (indentation + '.byte'.ljust(12) + '${:02X}'.format(opcode)).ljust(40 + len(indentation))
            to_write += '; {:06X}/{:02X}\n'.format(self.snes_pc, opcode)
            self.out_file.write(to_write)
            return

        op_addr = self.snes_pc

        mnemonic, types = OPCODES[opcode]
        types = types.split()

        bytes_ = bytearray([op_byte])
        operands = []
        for data_type in types:
            b = self.rom_file.read(DATA_TYPE_SIZES[data_type])
            bytes_ += b
            operands.append(self.datatype_to_str(data_type, b))

        if waited > 0:
            operands.append('WAIT #{}'.format(waited))

        if not self.was_linebreak:
            mnemonic = '\n' + mnemonic  # Add leading newline if previous line didn't have a line break
            self.was_linebreak = True

        comment = ''
        extra = ''

        if opcode == 0x07:  # ASMCALL
            address = int.from_bytes(bytes_[1:], byteorder='little')
            asm_func = self.asm_functions.get(address, None)
            if asm_func:
                DIRECTIVES = ('.byte', '.word', '.long', '.dword')
                comment = ' // ' + asm_func['comment'] if asm_func['comment'] else ''
                
                # Fucking hell this is horrible
                for p in asm_func['params']:
                    if p == 'varargs':
                        count = self.read_rom(1)
                        
                        self.pc = self.rom_file.tell()
                        extra += (indentation + '.byte'.ljust(12) + str(count)).ljust(40 + len(indentation))
                        extra += '; {:06X}/{:02X}\n'.format(self.snes_pc, count)
                        
                        for i in range(count):
                            self.pc = self.rom_file.tell()
                            b = self.rom_file.read(2)
                            addr = int.from_bytes(b, byteorder='little')
                            extra += (indentation + '.word'.ljust(12) + str(addr)).ljust(40 + len(indentation))
                            extra += '; {:06X}/{}\n'.format(self.snes_pc, b.hex().upper())
                    else:
                        self.pc = self.rom_file.tell()
                        data_size = DATA_TYPE_SIZES[p]
                        b = self.rom_file.read(data_size)

                        # Print the parameter's symbol if it exists; this really eases readability
#                        d = int.from_bytes(b, byteorder='little')
#                        if d in self.symbols:
#                            arg = self.symbols[d]
#                        else:
                        arg = self.datatype_to_str(p, b)
                        arg = arg.replace('#', '')
                        extra += (indentation + DIRECTIVES[data_size - 1].ljust(12) + arg).ljust(40 + len(indentation))
                        extra += '; {:06X}/{}\n'.format(self.snes_pc, b.hex().upper())

            else:

                if address not in warning_addresses:
                    print('AT {:06X} -'.format(self.snes_pc), "WARNING: IDK ANYTHING ABOUT ASM FUNCTION {:06X}".format(address))
                    warning_addresses.append(address)


        elif opcode in (0x0E, 0x15, 0x19):  # BINOP
            # Now THIS is what I call hacky shit!
            if opcode == 0x15:
                op = bytes_[2]
            else:
                op = bytes_[3]
            if op in (0, 1, 2, 3):
                operands[1] = BINOPS[op]
                mnemonic = mnemonic.replace('BIN_OP', BINOPS[op])
                
                if op == 2:  # ADD, change operand type from HEXADECIMAL immediate to DECIMAL immediate
                    data_type = 'imm_s8' if opcode == 0x19 else 'imm_s16'
                    size = DATA_TYPE_SIZES[data_type]
                    self.rom_file.seek(-size, os.SEEK_CUR)
                    operands[-1] = self.datatype_to_str(data_type, self.rom_file.read(size))
        elif opcode in (0x11, 0x12):  # MULTIJMP, MULTIJSR
            count = bytes_[1]
                
            for i in range(count):
                self.pc = self.rom_file.tell()
                b = self.rom_file.read(2)
                addr = self.datatype_to_str('label_16', b)
                extra += (indentation + '.word'.ljust(12) + addr).ljust(40 + len(indentation))
                extra += '; {:06X}/{}\n'.format(self.snes_pc, b.hex().upper())
        elif opcode in (0x00, 0x05, 0x0A, 0x0D, 0x1C):  # END, RTL, HALT, ENDTASK, RTS
            self.indentation = self._indent
            indentation = ' ' * self.indentation
            self.was_linebreak = True
        elif opcode == 0x01:  # STARTLOOP
            self.indentation += self._indent
        elif opcode == 0x02:  # ENDLOOP
            self.indentation = max(self._indent, self.indentation - self._indent)
            indentation = ' ' * self.indentation
        elif opcode in (0x03, 0x1A):  # JML, JMP
            self.was_linebreak = True
            self.indentation = max(self._indent, self.indentation - self._indent)

        to_write = (indentation + mnemonic.ljust(12) + ','.join(operands)).ljust(40 + len(indentation))
        to_write += '; {:06X}/{}{}\n'.format(op_addr, bytes_.hex().upper(), comment)
        self.out_file.write(to_write + extra)


    def init_symbols(self):
        if self.sym_file:
            self.parse_sym_file()

        # Seek to the start of the "script entry points" pointer table
#        self.rom_file.seek(0x002785 + self.header_offset)

        # Add default symbols for each script entry point, if they've not been defined
#        for i in range(self.script_count):
#            address = self.read_rom(3)
#            if address not in self.symbols:
#                self.symbols[address] = 'Script{:04d}'.format(i)

        # BAD STUFF AHEAD, LOTS OF DUPLICATE CODE FROM "disasm_opcode"
        for start, end in SCRIPT_BLOCKS:
            self.rom_file.seek(start)
            self.pc = self.rom_file.tell()

            while self.pc < end:
                opcode = self.read_rom(1)

                if opcode >= 0x30:
                    opcode = (((opcode - 0x30) & 0xF8) >> 3) + 0x26  # Get the actual opcode from the "waited opcode" code

                if opcode >= len(OPCODES):
                    continue

                if opcode == 0x08:  # TASK
                    bank_mask = self.snes_pc & 0xFF0000
                    addr = bank_mask | self.read_rom(2)
                    if addr not in self.symbols:
                        self.symbols[addr] = f'TASK_{addr:06X}'
                elif opcode == 0x07:  # ASMCALL
                    addr = self.read_rom(3)
                    asm_func = self.asm_functions.get(addr, None)
                    if asm_func:
                        for p in asm_func['params']:
                            if p == 'varargs':
                                count = self.read_rom(1)
                                self.rom_file.read(count*2)  # Read and discard bytes
                            else:
                                data_size = DATA_TYPE_SIZES[p]
                                b = self.rom_file.read(data_size)  # Read and discard bytes
                elif opcode in (0x11, 0x12):  # MULTIJMP/MULTIJSR
                    count = self.read_rom(1)
                    self.rom_file.read(count*2)  # Read and discard bytes
                else:
                    types = OPCODES[opcode][1].split()
                    for data_type in types:
                        if data_type == 'label_16':
                            bank_mask = self.snes_pc & 0xFF0000
                            addr = bank_mask | self.read_rom(2)
                            if addr not in self.symbols:
                                self.symbols[addr] = f'L_{addr:06X}'
                        elif data_type == 'label_24':
                            addr = self.read_rom(3)
                            if addr not in self.symbols:
                                self.symbols[addr] = f'L_{addr:06X}'
                        else:
                            self.rom_file.read(DATA_TYPE_SIZES[data_type])  # Read and discard bytes

                self.pc = self.rom_file.tell()

    def parse_sym_file(self):
        for i, line in enumerate(self.sym_file):
            pre_comment = line.split(';', maxsplit=1)[0].strip()  # Get everything on the line before the comment
            if '=' in pre_comment:
                label, str_address = [s.strip() for s in pre_comment.split('=', maxsplit=1)]

                if not all(c in LABEL_CHARSET for c in label):
                    print('Ignoring line {} from {}: Invalid label name ({})'.format(i, self.sym_file.name, label), file=sys.stderr)
                    continue

                try:
                    address = int(str_address, 16)
                    self.symbols[address] = label
                except ValueError:
                    print('Ignoring line {} from {}: Invalid address ({})'.format(i, self.sym_file.name, str_address), file=sys.stderr)
            elif pre_comment:
                print('Ignoring line {} from {}: Invalid line'.format(i, self.sym_file.name), file=sys.stderr)

    def init_asm_functions(self):
        if not self.asm_functions_file:
            return

        address = None
        asm_function = None
        for i, line in enumerate(self.asm_functions_file):
            pre_comment = line.split(';', maxsplit=1)[0].strip()  # Get everything on the line before the comment
            if '=' in pre_comment:
                if address is None:
                    print('Ignoring line {} from {}: Attribute assignment without ASM_FUNCTION directive'.format(i, self.asm_functions_file.name), file=sys.stderr)
                    continue

                key, value = [s.strip() for s in pre_comment.split('=', maxsplit=1)]                
                if key == 'COMMENT':
                    self.asm_functions[address]['comment'] = value
                elif key == 'PARAMS':
                    self.asm_functions[address]['params'] = [s.strip() for s in value.split(',')]
                else:
                    print('Ignoring line {} from {}: Invalid attribute ({})'.format(i, self.asm_functions_file.name, key), file=sys.stderr)
            elif pre_comment:
                directive, arg = [s.strip() for s in pre_comment.split(maxsplit=1)]
                if directive == 'ASM_FUNCTION':
                    try:
                        address = int(arg, 16)
                        self.asm_functions[address] = {'comment': '', 'params': []}
                    except ValueError:
                        print('Ignoring line {} from {}: Invalid address ({})'.format(i, self.asm_functions_file.name, arg), file=sys.stderr)
                else:
                    print('Ignoring line {} from {}: Unknown directive ({})'.format(i, self.asm_functions_file.name, directive), file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symfile', help='the symbols definition file')
    parser.add_argument('-a', '--asmfuncfile', help='the asm functions definition file')
    parser.add_argument('romfile', help="the Arcana ROM file")
    parser.add_argument('outfile', help='the output file')
    args = parser.parse_args()

    rom_size = os.path.getsize(args.romfile)
    header_offset = rom_size % 0x010000
    if rom_size < 0x080000 or (header_offset != 0 and header_offset != 512):
        print("The file {} doesn't look like a valid Arcana ROM!".format(args.romfile), file=sys.stderr)
        sys.exit(1)

    rom_file = open(args.romfile, 'rb')
    out_file = open(args.outfile, 'w')
    sym_file = open(args.symfile, 'r') if args.symfile else None
    asm_funcs_file = open(args.asmfuncfile, 'r') if args.asmfuncfile else None

    rom_file.seek(0x7FC0 + header_offset)
    rom_name = rom_file.read(21)

    if rom_name != b'ARCANA'.ljust(21):
        print("The file {} doesn't look like a valid Arcana ROM!".format(args.romfile), file=sys.stderr)
        sys.exit(1)

    disassembler = Disassembler(rom_file, out_file, sym_file, asm_funcs_file, header_offset, LAST_SCRIPT, indent=4)
    disassembler.disassemble_all()

    rom_file.close()
    out_file.close()
    if sym_file:
        sym_file.close()

    with open('symbols_out.txt', 'w') as f:
        for k, v in disassembler.symbols.items():
            f.write('{:06X}: {}\n'.format(k, v))
