cd C:\Users\neuro\OneDrive\Desktop\hackathon
python -c "
import traceback
try:
    import backend.main
    print('main imported')
except Exception as e:
    traceback.print_exc()
"