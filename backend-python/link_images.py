#!/usr/bin/env python3
"""
Image Linking Script
Scans installux_arcelor directory and links images to articles in the database.
"""

import os
import mysql.connector
from pathlib import Path
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Empty password as per .env
    'database': 'erp_arts_alu',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / 'installux_arcelor'
RELATIVE_PATH_PREFIX = 'installux_arcelor'

def scan_images():
    """Scan installux_arcelor directory for PNG files."""
    if not IMAGES_DIR.exists():
        print(f"ERROR: Directory not found: {IMAGES_DIR}")
        return []
    
    images = []
    for file in IMAGES_DIR.glob('*.png'):
        # Extract article code from filename (e.g., "102.png" -> "102")
        code_art = file.stem.upper()  # Uppercase for case-insensitive matching
        relative_path = f"{RELATIVE_PATH_PREFIX}/{file.name}"
        images.append({
            'code_art': code_art,
            'filename': file.name,
            'relative_path': relative_path
        })
    
    return images

def link_images_to_articles():
    """Main function to link images to articles."""
    print("=" * 60)
    print("IMAGE LINKING SCRIPT")
    print("=" * 60)
    
    # Scan images
    print(f"\n1. Scanning images in {IMAGES_DIR}...")
    images = scan_images()
    print(f"   Found {len(images)} PNG files")
    
    if not images:
        print("   No images found. Exiting.")
        return
    
    # Connect to database
    print("\n2. Connecting to database...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Statistics
        stats = {
            'images_inserted': 0,
            'articles_linked': 0,
            'articles_not_found': [],
            'errors': []
        }
        
        print("\n3. Processing images...")
        for img in images:
            try:
                # Check if article exists (case-insensitive)
                cursor.execute(
                    "SELECT code_art FROM article WHERE UPPER(code_art) = %s",
                    (img['code_art'],)
                )
                article = cursor.fetchone()
                
                if not article:
                    stats['articles_not_found'].append(img['code_art'])
                    continue
                
                actual_code_art = article[0]  # Get actual case from DB
                
                # Insert image into image table
                cursor.execute(
                    """
                    INSERT INTO image (chemin, date_creation)
                    VALUES (%s, %s)
                    """,
                    (img['relative_path'], datetime.now())
                )
                image_id = cursor.lastrowid
                stats['images_inserted'] += 1
                
                # Update article with image ID
                cursor.execute(
                    """
                    UPDATE article
                    SET id_image = %s
                    WHERE code_art = %s
                    """,
                    (image_id, actual_code_art)
                )
                stats['articles_linked'] += 1
                
                if stats['articles_linked'] % 100 == 0:
                    print(f"   Processed {stats['articles_linked']} articles...")
                
            except Exception as e:
                stats['errors'].append(f"{img['code_art']}: {str(e)}")
        
        # Commit transaction
        conn.commit()
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"✓ Images inserted:     {stats['images_inserted']}")
        print(f"✓ Articles linked:     {stats['articles_linked']}")
        print(f"⚠ Articles not found: {len(stats['articles_not_found'])}")
        print(f"✗ Errors:              {len(stats['errors'])}")
        
        if stats['articles_not_found']:
            print(f"\nArticles without matching database entry (first 10):")
            for code in stats['articles_not_found'][:10]:
                print(f"  - {code}")
            if len(stats['articles_not_found']) > 10:
                print(f"  ... and {len(stats['articles_not_found']) - 10} more")
        
        if stats['errors']:
            print(f"\nErrors encountered:")
            for error in stats['errors'][:5]:
                print(f"  - {error}")
            if len(stats['errors']) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more")
        
        # Check articles without images
        cursor.execute(
            "SELECT COUNT(*) FROM article WHERE id_image IS NULL"
        )
        articles_without_images = cursor.fetchone()[0]
        print(f"\n📊 Articles without images: {articles_without_images}")
        
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)

if __name__ == '__main__':
    link_images_to_articles()
