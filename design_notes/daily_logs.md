# Feb 18, 2025
We have implement a baseline to upload metadata and embeddings for a single AP questions. At this point I believe this will be 
enough to test if our setup is good enough to help cache prompts. 

We may want to at this point cache the prompt however, for the sake of over optimizing at the begining I'd like to move on to 
implementing at least the FRQ generation. 

For this I hope to leverage just the terminal we will extract all front end to be hard coded, ie instead of working on the selection part for AP Calc AB and pulling relevat questions we will just filter as is for now and test a few prompts to ensure generation is good. 

I believe I can get this done this week. Right now I'm unsure if it would be best to just hard code the routing, or should I abstract this out now to a agent. I might need to play arond with this more off the plane. 