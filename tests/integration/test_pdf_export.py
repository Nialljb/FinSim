"""
Test script to verify Kaleido PDF export functionality
Run this after deployment to test if PDF export is working
"""

import sys

def test_kaleido():
    """Test if Kaleido can convert Plotly charts to images"""
    print("=" * 60)
    print("Testing Kaleido PDF Export Functionality")
    print("=" * 60)
    
    # Test 1: Import Plotly
    print("\n[1/4] Testing Plotly import...")
    try:
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Plotly: {e}")
        return False
    
    # Test 2: Import Plotly IO
    print("\n[2/4] Testing Plotly IO import...")
    try:
        import plotly.io as pio
        print("✅ Plotly IO imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Plotly IO: {e}")
        return False
    
    # Test 3: Create test figure
    print("\n[3/4] Creating test Plotly figure...")
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines'))
        fig.update_layout(title='Test Chart')
        print("✅ Test figure created successfully")
    except Exception as e:
        print(f"❌ Failed to create figure: {e}")
        return False
    
    # Test 4: Convert to image (this is where Kaleido is used)
    print("\n[4/4] Converting figure to image (testing Kaleido)...")
    try:
        img_bytes = pio.to_image(fig, format='png', width=800, height=600)
        print(f"✅ Image conversion successful! Generated {len(img_bytes):,} bytes")
        
        # Additional test: Try different formats
        print("\n[BONUS] Testing different image formats...")
        formats_to_test = ['png', 'jpg', 'svg']
        for fmt in formats_to_test:
            try:
                test_bytes = pio.to_image(fig, format=fmt, width=400, height=300)
                print(f"  ✅ {fmt.upper()}: {len(test_bytes):,} bytes")
            except Exception as e:
                print(f"  ❌ {fmt.upper()}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to convert to image: {e}")
        print("\nThis is the Kaleido error. Common causes:")
        print("  1. Missing system dependencies (Chrome/Chromium libraries)")
        print("  2. Kaleido not installed correctly")
        print("  3. Permission issues in containerized environment")
        print("\nTroubleshooting:")
        print("  - Check that render-build.sh ran successfully")
        print("  - Verify all apt-get packages installed")
        print("  - Check Render logs for build errors")
        return False

def test_reportlab():
    """Test if ReportLab can create PDFs"""
    print("\n" + "=" * 60)
    print("Testing ReportLab PDF Generation")
    print("=" * 60)
    
    print("\n[1/2] Testing ReportLab import...")
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        print("✅ ReportLab imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ReportLab: {e}")
        return False
    
    print("\n[2/2] Creating test PDF...")
    try:
        import io
        from reportlab.platypus import SimpleDocTemplate, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import letter
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph("Test PDF Document", styles['Title'])]
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        print(f"✅ PDF creation successful! Generated {len(pdf_bytes):,} bytes")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create PDF: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🧪 FinSim PDF Export Test Suite\n")
    
    kaleido_ok = test_kaleido()
    reportlab_ok = test_reportlab()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Kaleido (Chart conversion): {'✅ PASS' if kaleido_ok else '❌ FAIL'}")
    print(f"ReportLab (PDF creation):   {'✅ PASS' if reportlab_ok else '❌ FAIL'}")
    
    if kaleido_ok and reportlab_ok:
        print("\n🎉 SUCCESS! PDF export should work correctly.")
        print("\nYou can now:")
        print("  1. Run simulations in the app")
        print("  2. Click 'Export to PDF'")
        print("  3. Download and view PDF reports")
        return 0
    else:
        print("\n⚠️  ISSUES DETECTED! PDF export may not work.")
        print("\nNext steps:")
        if not kaleido_ok:
            print("  1. Check render-build.sh ran successfully")
            print("  2. Verify system dependencies installed")
            print("  3. Check Render logs for errors")
        if not reportlab_ok:
            print("  1. Verify requirements.txt includes reportlab>=4.0.0")
            print("  2. Re-install Python packages")
        print("\nSee FIX_PDF_EXPORT_RENDER.md for detailed troubleshooting")
        return 1

if __name__ == "__main__":
    sys.exit(main())
