Step 1: open url http://localhost:5000/hinglish 
using `Playwright` mcp server tools

Step 2: upload a file `books\brida.txt`

Step 3: wait for translation to complete
Step 4: download the translated file, download click button should work
Step 5: verify the translated file is in Hindi Roman language (Hinglish)
example 1: "what are you doing" should be translated to "aap kya kar rahe ho"
example 2: "this is a book" should be translated to "yeh ek kitab hai"
Step 6: if not translated correctly, fix the code and  repeat from step 1
Step 7: if translated correctly, end the test
