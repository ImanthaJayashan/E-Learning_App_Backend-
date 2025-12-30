import json
import csv
from pathlib import Path
from datetime import datetime
import numpy as np




def main():
    import argparse
    parser = argparse.ArgumentParser(description='Extract iris metrics from received sample images')
    parser.add_argument('--json', default='received_samples/inference_results.json', help='JSON file with inference results')
    parser.add_argument('--output-csv', default='iris_metrics.csv', help='Output CSV file')
    args = parser.parse_args()
    
    json_file = Path(args.json)
    if not json_file.exists():
        print(f"JSON file not found: {json_file}")
        print("\nNote: The Flask server saves metrics to inference_results.json when predictions are made.")
        print("You can also manually run the web app to test and capture predictions.")
        return
    
    
    # Load results from JSON
    try:
        with open(json_file, 'r') as f:
            results_data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return
    
    # Parse results and build CSV
    all_metrics = []
    if isinstance(results_data, list):
        records = results_data
    else:
        records = results_data.get('records', [results_data])
    
    print(f"Processing {len(records)} inference results...")
    for i, record in enumerate(records):
        print(f"  [{i+1}/{len(records)}] {record.get('timestamp', 'unknown')}...", end=' ')
        
        # Check if metrics are present
        if 'iris_metrics' in record:
            metrics_data = record['iris_metrics']
            row = {
                'timestamp': record.get('timestamp', ''),
                'prediction': record.get('label', ''),
                'confidence': record.get('confidence', 0),
                'left_iris_cx': metrics_data.get('left', {}).get('center', {}).get('x', ''),
                'left_iris_cy': metrics_data.get('left', {}).get('center', {}).get('y', ''),
                'left_iris_radius': metrics_data.get('left', {}).get('r', ''),
                'left_gaze_ratio': metrics_data.get('left', {}).get('gazeX', ''),
                'left_ear': metrics_data.get('left', {}).get('ear', ''),
                'right_iris_cx': metrics_data.get('right', {}).get('center', {}).get('x', ''),
                'right_iris_cy': metrics_data.get('right', {}).get('center', {}).get('y', ''),
                'right_iris_radius': metrics_data.get('right', {}).get('r', ''),
                'right_gaze_ratio': metrics_data.get('right', {}).get('gazeX', ''),
                'right_ear': metrics_data.get('right', {}).get('ear', ''),
                'ipd_px': metrics_data.get('ipd', ''),
            }
            all_metrics.append(row)
            print(f"✓ {row['prediction']} (conf={row['confidence']:.3f})")
        else:
            print("✗ No iris metrics in record")
    
    
    # Write to CSV
    if all_metrics:
        output_path = Path(args.output_csv)
        fieldnames = list(all_metrics[0].keys())
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_metrics)
        
        print(f"\n✓ Saved {len(all_metrics)} records to {output_path.resolve()}")
        
        # Print summary statistics
        if all_metrics:
            gaze_ratios_l = [float(m['left_gaze_ratio']) for m in all_metrics if m.get('left_gaze_ratio')]
            gaze_ratios_r = [float(m['right_gaze_ratio']) for m in all_metrics if m.get('right_gaze_ratio')]
            ears_l = [float(m['left_ear']) for m in all_metrics if m.get('left_ear')]
            ears_r = [float(m['right_ear']) for m in all_metrics if m.get('right_ear')]
            ipds = [float(m['ipd_px']) for m in all_metrics if m.get('ipd_px')]
            
            print(f"\nSummary Statistics:")
            
            if gaze_ratios_l:
                print(f"  Left gaze ratio:  mean={np.mean(gaze_ratios_l):.3f}, std={np.std(gaze_ratios_l):.3f}")
            if gaze_ratios_r:
                print(f"  Right gaze ratio: mean={np.mean(gaze_ratios_r):.3f}, std={np.std(gaze_ratios_r):.3f}")
            if ears_l:
                print(f"  Left EAR:  mean={np.mean(ears_l):.4f}, std={np.std(ears_l):.4f}")
            if ears_r:
                print(f"  Right EAR: mean={np.mean(ears_r):.4f}, std={np.std(ears_r):.4f}")
            if ipds:
                print(f"  IPD (interpupillary): mean={np.mean(ipds):.2f}px, std={np.std(ipds):.2f}px")
    else:
        print("✗ No metrics found in JSON records")


if __name__ == '__main__':
    main()
