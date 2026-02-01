def debug_blob_issue(driver):
    """
    Simple debug function to print Blob URL info
    """
    print("\n🔍 DEBUGGING BLOB URL ISSUE:")
    print("=" * 50)
    
    # 1. Check current URL
    print(f"1. Current URL: {driver.current_url}")
    
    # 2. Check for any Blob URLs on page
    blob_info = driver.execute_script("""
        const results = {
            totalAnchors: document.querySelectorAll('a').length,
            blobAnchors: [],
            blobIframes: [],
            blobObjects: []
        };
        
        // Check all anchors
        document.querySelectorAll('a').forEach(anchor => {
            if (anchor.href && anchor.href.startsWith('blob:')) {
                results.blobAnchors.push({
                    href: anchor.href,
                    download: anchor.download,
                    text: anchor.textContent.substring(0, 50)
                });
            }
        });
        
        // Check iframes
        document.querySelectorAll('iframe').forEach(iframe => {
            if (iframe.src && iframe.src.startsWith('blob:')) {
                results.blobIframes.push(iframe.src);
            }
        });
        
        // Check objects
        document.querySelectorAll('object').forEach(obj => {
            if (obj.data && obj.data.startsWith('blob:')) {
                results.blobObjects.push(obj.data);
            }
        });
        
        return results;
    """)
    
    print(f"2. Found {blob_info['totalAnchors']} total anchor tags")
    print(f"3. Found {len(blob_info['blobAnchors'])} Blob URL anchors")
    print(f"4. Found {len(blob_info['blobIframes'])} Blob URL iframes")
    print(f"5. Found {len(blob_info['blobObjects'])} Blob URL objects")
    
    # Print details of Blob anchors
    if blob_info['blobAnchors']:
        print("\n📄 Blob Anchor Details:")
        for i, anchor in enumerate(blob_info['blobAnchors']):
            print(f"   Anchor {i+1}:")
            print(f"     URL: {anchor['href'][:80]}...")
            print(f"     Download attr: {anchor['download']}")
            print(f"     Text: {anchor['text']}")
    
    # 3. Check if window has any export/data variables
    window_vars = driver.execute_script("""
        const exportVars = [];
        for (const key in window) {
            if (key.toLowerCase().includes('export') || 
                key.toLowerCase().includes('csv') || 
                key.toLowerCase().includes('data') ||
                key.toLowerCase().includes('blob')) {
                exportVars.push(key);
            }
        }
        return exportVars.slice(0, 20);  // First 20 only
    """)
    
    print(f"\n6. Window variables related to export/data: {window_vars}")
    
    # 4. Try to create a test Blob to see if downloads work
    test_result = driver.execute_script("""
        try {
            // Create a test Blob
            const testData = 'test,csv,data\\n1,2,3\\n4,5,6';
            const blob = new Blob([testData], {type: 'text/csv'});
            const blobUrl = URL.createObjectURL(blob);
            
            // Create and click a download link
            const a = document.createElement('a');
            a.href = blobUrl;
            a.download = 'test_download.csv';
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            setTimeout(() => {
                URL.revokeObjectURL(blobUrl);
                document.body.removeChild(a);
            }, 100);
            
            return 'Test Blob created successfully: ' + blobUrl.substring(0, 50) + '...';
        } catch (error) {
            return 'Test Blob failed: ' + error.message;
        }
    """)
    
    print(f"\n7. Test Blob creation: {test_result}")
    
    print("=" * 50)
    return blob_info