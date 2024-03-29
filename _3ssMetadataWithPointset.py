import os
import pandas as pd
import json
import numpy as np

def convert_to_json_serializable(value):
    if isinstance(value, np.int64):
        return int(value)
    elif pd.isna(value):
        return ""
    else:
        return value

def generate_metadata(excel_file_path):
    try:
        df = pd.read_excel(excel_file_path, sheet_name=None)
        assets_sheet = df['Assets']
        asset_payload_types_sheet = df['Asset Payload Types']
        valid_asset_types = set(asset_payload_types_sheet['points_type'].unique())

        for index, row in assets_sheet.iterrows():
            instance_name = row['mqtt.physical_tag.asset.instance_name']
            asset_type = row['mqtt.points']
            if asset_type not in valid_asset_types:
                continue

            # Create a dictionary to store the asset metadata
            asset_metadata = {
                "instname": instance_name,
                "vendorname": convert_to_json_serializable(row['mqtt.physical_tag.asset.manufacturer']),
                "modelname": convert_to_json_serializable(row['mqtt.physical_tag.asset.model']),
                "firmware": convert_to_json_serializable(row['mqtt.physical_tag.asset.firmware_version']),
                "software_version": convert_to_json_serializable(row['mqtt.physical_tag.asset.software_version']),
                "serial_number": convert_to_json_serializable(row['mqtt.physical_tag.asset.serial_number']),
                "eng_unit_type": convert_to_json_serializable(row['mqtt.physical_tag.asset.eng_unit_type']),
                "eng_asset_tag": convert_to_json_serializable(row['mqtt.physical_tag.asset.eng_asset_tag']),
                "location": {
                    "x_coord": convert_to_json_serializable(row['mqtt.physical_tag.asset.location.x_coord']),
                    "y_coord": convert_to_json_serializable(row['mqtt.physical_tag.asset.location.y_coord'])
                },
                "relationships": {
                    "hasLocation": convert_to_json_serializable(row['mqtt.physical_tag.asset.relationships.hasLocation']),
                    "isAssociatedWith": convert_to_json_serializable(row['mqtt.physical_tag.asset.relationships.isAssociatedWith']),
                    "isPartOf": convert_to_json_serializable(row['mqtt.physical_tag.asset.relationships.isPartOf']),
                    "isFedBy": [convert_to_json_serializable(fed_by.strip()) for fed_by in str(row['mqtt.physical_tag.asset.relationships.isFedBy']).split(',')]
                }
            }

            pointset_data = {"points": {}}

            for _, asset_row in asset_payload_types_sheet.iterrows():
                point_name = asset_row['mqtt.pointset.points']
                point_units = asset_row['mqtt.pointset.units']
                point_type = asset_row['points_type']

                if point_type == asset_type:
                    pointset_data["points"][point_name] = {"units": point_units}

            asset_folder_path = os.path.join(os.path.dirname(excel_file_path), instance_name)
            os.makedirs(asset_folder_path, exist_ok=True)

            metadata_file_path = os.path.join(asset_folder_path, 'metadata.json')
            with open(metadata_file_path, 'w') as file:
                json.dump(asset_metadata, file, indent=2)
            print(f"Metadata file successfully created for instance {instance_name}: {metadata_file_path}")

            if pointset_data["points"]:
                pointset_file_path = os.path.join(asset_folder_path, 'pointset.json')
                with open(pointset_file_path, 'w') as pointset_file:
                    json.dump(pointset_data, pointset_file, indent=2)
                print(f"Pointset file successfully created for asset {instance_name}: {pointset_file_path}")

    except Exception as e:
        print(f"Error: {e}")

# Replace 'your_excel_file.xlsx' with the path to your Excel file
generate_metadata('')
