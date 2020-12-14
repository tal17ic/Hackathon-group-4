#api 2.7, integrated thermocycler module

from opentrons import  simulate
protocol = simulate.get_protocol_api('2.7')
 

#metadata
metadata = {
     'apiLevel': '2.7',
     'protocolName': 'CLIP',
     'author': 'group four',
     'description': 'Implements linker ligation reactions using an opentrons OT-2.'}

 


#start from here
def run(protocol):
    def clip(
            prefixes_wells,
            prefixes_plates,
            suffixes_wells,
            suffixes_plates,
            parts_wells,
            parts_plates,
            parts_vols,
            water_vols,
            tiprack_type="opentrons_96_tiprack_20ul"):
    
        
        ### Constants
        
        #Tiprack
        INITIAL_TIP = 'A1'
        CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9']
        
        # Pipettes
        PIPETTE_TYPE = 'p20_single_gen2'
        PIPETTE_MOUNT = 'right'

        # Source Plates
        SOURCE_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
       
        # Tube Rack
        TUBE_RACK_TYPE = 'usascientific_12_reservoir_22ml'
        TUBE_RACK_POSITION = '4'
        MASTER_MIX_WELL = 'A1'
        WATER_WELL = 'A2'
        MASTER_MIX_VOLUME = 20
        
        # Mix settings
        LINKER_MIX_SETTINGS = (1, 3)
        PART_MIX_SETTINGS = (4, 5)
        
        
        
    
        ### Loading Tiprack
        
        # Calculates whether one, two, or three tipracks are needed, which are in slots 3, 6, and 9 respectively
            # for single construct example, X tipracks are needed
        total_tips = 4 * len(parts_wells)
        letter_dict = {'A': 0, 'B': 1, 'C': 2,
                       'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
        tiprack_1_tips = (
            13 - int(INITIAL_TIP[1:])) * 8 - letter_dict[INITIAL_TIP[0]]
        if total_tips > tiprack_1_tips:
            tiprack_num = 1 + (total_tips - tiprack_1_tips) // 96 + \
                (1 if (total_tips - tiprack_1_tips) % 96 > 0 else 0)
        else:
            tiprack_num = 1
        slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]
        
        # loads the correct number of tipracks
            #for single construct example, X tipracks are loaded into X
        tipracks = [protocol.load_labware(tiprack_type, slot) for slot in slots]
        # old code:
        # tipracks = [labware.load(tiprack_type, slot) for slot in slots]

 


        ### Load Pipette
        
        # checks if it's a P20 Single pipette
        if PIPETTE_TYPE != 'p20_single_gen2':
            print('Define labware must be changed to use', PIPETTE_TYPE)
            exit()
        # old code:
        # if PIPETTE_TYPE != 'P10_single':
            # print('Define labware must be changed to use', PIPETTE_TYPE)
            # exit()
        
        # Loads pipette according to variables assigned above
        pipette = protocol.load_instrument(PIPETTE_TYPE, mount=PIPETTE_MOUNT, tip_racks=tipracks)
            # ADD start_at_tip TO THE NEW CODE AS WELL? It's not in apiV2 documentation!
        # old code:
        # pipette = instruments.P10_Single(mount=PIPETTE_MOUNT, tip_racks=tipracks)
        # pipette.start_at_tip(tipracks[0].well(INITIAL_TIP))
    
    
        ### Loading Source Plates
        
        # makes a source plate key according to where the prefixes, suffixes, and parts are
            # for the single construct example, source_plate_key is [2,5]
            # prefixes and suffixes on plate 2, parts on plate 5
        source_plates = {}
        source_plates_keys = list(set((prefixes_plates + suffixes_plates + parts_plates)))
        
        # loads the plates according to the source plate key
            # for the single construct example, loads plates into 2 and 5
        for key in source_plates_keys:
            source_plates[key]=protocol.load_labware(SOURCE_PLATE_TYPE, key)
            # old code:
            # source_plates[key] = labware.load(SOURCE_PLATE_TYPE, key)
        
        
        ### Load Destination Plate
        
       
         #thermocycler block(destination_plate), default slot:7,8,10,11
        tc_mod = protocol.load_module('Thermocycler Module')
        destination_plate = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
        # old code:
        # destination_plate = labware.load(DESTINATION_PLATE_TYPE, DESTINATION_PLATE_POSITION)
        
        # Defines where the destination wells are within the destination plate
            # for single construct example, the destination wells are A1 to E1 (5 parts)
        destination_wells = destination_plate.wells()[0:len(parts_wells)]
        # old code:
        # destination_wells = destination_plate.wells(INITIAL_DESTINATION_WELL, length=int(len(parts_wells)))
        
        
        ### Load Tube Rack
        
        # Loads tube rack according to variables assigned above
            # for single construct example, tube rack position is 4
        tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        # old code:
        # tube_rack = labware.load(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        
        # Defines positions of master mix and water within the tube rack
            # for single construct example, master mix is in A1 and water is in A2
        master_mix = tube_rack.wells(MASTER_MIX_WELL)
        water = tube_rack.wells(WATER_WELL)
        
        
        #open lid and add reagent directly to the thermocycler block
        tc_mod.open_lid()
        
        ### Transfers
        
        # transfer master mix into destination wells
            # added blowout into destination wells
            # added pick up tip and return tip
        pipette.pick_up_tip()
        pipette.transfer(MASTER_MIX_VOLUME, master_mix, destination_wells, blow_out=True, new_tip='never')
        pipette.return_tip()
        # old code:
        # pipette.pick_up_tip()
        # pipette.transfer(MASTER_MIX_VOLUME, master_mix, destination_wells, new_tip='never')
        # pipette.drop_tip()
        
        # transfer water into destination wells
            # added blowout into destination wells
        pipette.transfer(water_vols, water, destination_wells, blow_out=True,  new_tip='always')
        # old code:
        # pipette.transfer(water_vols, water, destination_wells, new_tip='always')
        
        #transfer prefixes, suffixes, and parts into destination wells
            # added blowout into destination wells
        for clip_num in range(len(parts_wells)):
            pipette.transfer(1, source_plates[prefixes_plates[clip_num]].wells(prefixes_wells[clip_num]), destination_wells[clip_num], blow_out=True,  mix_after=LINKER_MIX_SETTINGS)
            pipette.transfer(1, source_plates[suffixes_plates[clip_num]].wells(suffixes_wells[clip_num]), destination_wells[clip_num], blow_out=True,  mix_after=LINKER_MIX_SETTINGS)
            pipette.transfer(parts_vols[clip_num], source_plates[parts_plates[clip_num]].wells(parts_wells[clip_num]), destination_wells[clip_num], blow_out=True,  mix_after=PART_MIX_SETTINGS)
        # old code:
        # for clip_num in range(len(parts_wells)):
            # pipette.transfer(1, source_plates[prefixes_plates[clip_num]].wells(prefixes_wells[clip_num]),
                             # destination_wells[clip_num], mix_after=LINKER_MIX_SETTINGS)
            # pipette.transfer(1, source_plates[suffixes_plates[clip_num]].wells(suffixes_wells[clip_num]),
                             # destination_wells[clip_num], mix_after=LINKER_MIX_SETTINGS)
            # pipette.transfer(parts_vols[clip_num], source_plates[parts_plates[clip_num]].wells(parts_wells[clip_num]),
                             # destination_wells[clip_num], mix_after=PART_MIX_SETTINGS)
              
            # the run function will first define the CLIP function, and then run CLIP with the dictionary produced by DNA-BOT
        
    
    
        #run clip reaction in thermocycler block
        tc_mod.close_lid()
        tc_mod.set_lid_temperature(37)#set the lid temperature to 37˚C before running clip reaction
        profile = [
             {'temperature': 37, 'hold_time_minutes': 2},
             {'temperature': 20, 'hold_time_minutes': 1}]#run digestion and ligation for 20 cycles
        tc_mod.execute_profile(steps=profile, repetitions=20,block_max_volume=30)
        tc_mod.set_block_temperature(60, hold_time_minutes=10, block_max_volume=30)#60˚C for 10 minutes
        tc_mod.open_lid()#complete clip reaction
 
    
    
    
    clip(**clips_dict)
    
run(protocol)

for c in protocol.commands():
    print(c)