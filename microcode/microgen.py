#!/usr/bin/env python3
import argparse
import os
from typing import List, Dict, Any, Tuple
from microdef import *



# Reverse lookup: bit position to field name
FIELD_BIT_MAP = {}
for field_name, field_def in FIELD_DEFINITIONS.items():
    start_bit, end_bit = field_def["bits"]
    for bit in range(start_bit, end_bit + 1):
        FIELD_BIT_MAP[bit] = field_name

def parse_field_value(field_str: str) -> tuple:
    if '=' in field_str:
        field, value = field_str.split('=', 1)
        return field.strip(), int(value)
    return field_str.strip(), FIELD_DEFINITIONS[field_str.strip()]["value"]

def build_microinstruction(fields: List[str]) -> int:
    instruction = 0
    
    for field_spec in fields:
        field_name, value = parse_field_value(field_spec)
        
        if field_name not in FIELD_DEFINITIONS:
            raise ValueError(f"Unknown field: {field_name}")
        
        field_def = FIELD_DEFINITIONS[field_name]
        start_bit, end_bit = field_def["bits"]
        bit_width = end_bit - start_bit + 1
        
        # Check if value fits in the field
        max_value = (1 << bit_width) - 1
        if value > max_value:
            raise ValueError(f"Value {value} too large for field {field_name} "
                           f"(max {max_value})")
        
        # Set the bits in the instruction
        instruction |= (value << start_bit)
    
    return instruction

def disassemble_microinstruction(instruction: int) -> List[str]:
    fields = []
    
    # Check single-bit fields
    for field_name, field_def in FIELD_DEFINITIONS.items():
        start_bit, end_bit = field_def["bits"]
        
        if start_bit == end_bit:  # Single-bit field
            if instruction & (1 << start_bit):
                fields.append(field_name)
        else:  # Multi-bit field
            mask = (1 << (end_bit - start_bit + 1)) - 1
            value = (instruction >> start_bit) & mask
            if value != 0:  # Only show if non-zero
                fields.append(f"{field_name}={value}")
    
    return fields

def generate_microcode_rom(microcode: Dict[int, List[List[str]]], max_uPC_steps: int = 16) -> List[int]:
    rom_size = 256 * max_uPC_steps
    rom = [0] * rom_size
    
    for opcode, uPC_steps in microcode.items():
        if opcode >= 256:
            continue
            
        for uPC, fields in enumerate(uPC_steps):
            if uPC >= max_uPC_steps:
                break
                
            #address = (opcode << 8) | uPC
            address = (opcode * max_uPC_steps) + uPC
            if address < rom_size:
                rom[address] = build_microinstruction(fields)
    
    return rom

def verify_microcode(microcode: Dict[int, List[List[str]]], rom_data: List[int], max_uPC_steps: int = 16):
    print("Verification Results:")
    print("=" * 60)
    
    all_good = True
    verified_count = 0
    
    for opcode, expected_steps in microcode.items():
        if opcode >= 256:
            continue
            
        print(f"\nOpcode 0x{opcode:02X}:")
        print("-" * 40)
        
        for uPC, expected_fields in enumerate(expected_steps):
            if uPC >= max_uPC_steps:
                break
                
            #address = (opcode << 8) | uPC
            address = (opcode * max_uPC_steps) + uPC
            if address >= len(rom_data):
                continue
                
            # Get the actual instruction from ROM
            actual_instruction = rom_data[address]
            
            # Disassemble back to fields
            actual_fields = disassemble_microinstruction(actual_instruction)
            
            # Build expected instruction for comparison
            expected_instruction = build_microinstruction(expected_fields)
            
            # Check if they match
            matches = actual_instruction == expected_instruction
            
            print(f"  0x{address:03X}: ", end="")
            if matches:
                print("✓ ", end="")
                verified_count += 1
            else:
                print("✗ ", end="")
                all_good = False
            
            print(f"Expected: {expected_fields}")
            print(f"          Actual:   {actual_fields}")
            
            if not matches:
                print(f"          Instruction: 0x{actual_instruction:08X} (expected: 0x{expected_instruction:08X})")
    
    print(f"\nVerification Summary:")
    print(f"  Instructions verified: {verified_count}")
    print(f"  All match: {'✓ YES' if all_good else '✗ NO'}")
    
    return all_good

def intel_hex_record(address: int, data: List[int], record_type: int = 0) -> str:
    byte_count = len(data)
    checksum = byte_count + (address >> 8) + (address & 0xFF) + record_type
    hex_data = ''.join(f"{byte:02X}" for byte in data)
    
    for byte in data:
        checksum += byte
    
    checksum = (-checksum) & 0xFF
    return f":{byte_count:02X}{address:04X}{record_type:02X}{hex_data}{checksum:02X}"

def generate_hex_files(rom_data: List[int], output_prefix: str, bytes_per_record: int = 16):
    if not rom_data:
        return
    
    os.makedirs(os.path.dirname(output_prefix) if os.path.dirname(output_prefix) else '.', exist_ok=True)
    
    for byte_idx in range(4):
        filename = f"{output_prefix}_byte{byte_idx}.hex"
        records = []
        
        for base_address in range(0, len(rom_data), bytes_per_record):
            chunk = rom_data[base_address:base_address + bytes_per_record]
            byte_chunk = []
            for word in chunk:
                byte_value = (word >> (byte_idx * 8)) & 0xFF
                byte_chunk.append(byte_value)
            
            if byte_chunk:
                records.append(intel_hex_record(base_address, byte_chunk))
        
        records.append(intel_hex_record(0, [], 1))
        
        with open(filename, 'w') as f:
            f.write('\n'.join(records))
        
        print(f"Generated: {filename}")

def print_disassembly(rom_data: List[int], microcode: Dict[int, List[List[str]]], max_uPC_steps: int = 16):
    print("\nMicrocode Disassembly:")
    print("=" * 80)
    
    # Only disassemble addresses that have microcode defined
    for opcode in sorted(microcode.keys()):
        if opcode >= 256:
            continue
            
        print(f"\nOpcode 0x{opcode:02X}:")
        for uPC in range(max_uPC_steps):
            address = (opcode << 8) | uPC
            if address >= len(rom_data):
                continue
                
            instruction = rom_data[address]
            if instruction == 0 and uPC >= len(microcode.get(opcode, [])):
                continue  # Skip unused uPC steps
                
            fields = disassemble_microinstruction(instruction)
            print(f"  0x{address:03X}: {fields}")
            
            # Stop if we've reached the end of this opcode's microcode
            if uPC >= len(microcode.get(opcode, [])) - 1 and instruction == 0:
                break

def main():
    parser = argparse.ArgumentParser(description="Generate Intel HEX ROM files from microcode")
    parser.add_argument("--output", "-o", default="rom", help="Output file prefix")
    parser.add_argument("--max-upc", type=int, default=16, help="Maximum uPC steps per opcode")
    parser.add_argument("--verify", "-v", action="store_true", help="Verify generated ROM against microcode")
    parser.add_argument("--disassemble", "-d", action="store_true", help="Disassemble the generated ROM")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress non-essential output")
    
    args = parser.parse_args()
    
    # Generate the microcode ROM
    rom_data = generate_microcode_rom(MICROCODE, args.max_upc)
    
    # Verify if requested
    if args.verify:
        success = verify_microcode(MICROCODE, rom_data, args.max_upc)
        if not success and not args.quiet:
            print("\nWARNING: Verification failed! Check your microcode definitions.")
    
    # Generate HEX files
    generate_hex_files(rom_data, args.output)
    
    # Disassemble if requested
    if args.disassemble:
        print_disassembly(rom_data, MICROCODE, args.max_upc)
    
    if not args.quiet:
        total_size = len(rom_data)
        print(f"\nSummary:")
        print(f"  ROM size: {total_size} addresses (0x000-0x{total_size-1:03X})")
        print(f"  Total bytes: {total_size * 4}")
        print(f"  Output files: {args.output}_byte[0-3].hex")

if __name__ == "__main__":
    main()
