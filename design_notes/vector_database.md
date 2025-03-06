## What is the point of the vector database 
The point of the vector database in the case really just to hold information relatvant to the AP score to utilize few-shot prompting 
1) to generate new and unique FRQs 
2) to understand the criteria for review 

so for use we really do not care about the layout of the pdf or any visual infomrat just the text. Additionally, given the idea that later on we also will not care about visual information at this point only vectorizing the text will actually help us reduce complexity of the model and leverae a uni-modal text model insead of relying on a multi modal model. 


### Proof of concept vs MVP 
at this point the fastest path forward is to just pull the relevant information and generate the vector DB manually however we will have to come back to this to generate a ideal pipeline later on for scalability

Below is a revised Markdown document that outlines the database tables, columns, keys, and descriptions in a clear, organized format:

# Vector DB Setup

This document outlines the tables and their structures for our vector database, which supports the following data types:

- **FRQ** (Free-Response Questions)
- **Scoring Guidelines**
- **Chief Reader Report**
- **Sample Responses**

---

## Table: Class

| Column     | Type | Key         | Description                            |
|------------|------|-------------|----------------------------------------|
| class_id   | int  | Primary Key | Unique identifier for each class.      |
| class_name | str  |             | Name of the class.                     |

**Description:**  
This table maps all available classes.

---

## Table: FRQ

| Column | Type | Key         | Description                                          |
|--------|------|-------------|------------------------------------------------------|
| FRQ_id | int  | Primary Key | Unique identifier for each FRQ.                      |
| class_id | int | Foreign Key | References the associated class in the Class table.  |
| FRQ    | str (optional) |             | The free-response question text.                   |
| embeddings| vector |           | tokenized embedding vectors of FRQ

**Description:**  
This table tracks all available free-response questions for few-shot prompting.

---

## Table: Scoring Guideline

| Column              | Type | Key         | Description                                                                           |
|---------------------|------|-------------|---------------------------------------------------------------------------------------|
| scoring_id          | int  | Primary Key | Unique identifier for each scoring guideline entry.                                  |
| class_id            | int  | Foreign Key | References the associated class in the Class table.                                   |
| question_id         | int  | Foreign Key | References the related question in the FRQ table.                                      |
| scoring_guide_lines | str (optional)  |             | The text for the scoring guidelines.                                                  |
| embeddings| vector |           | tokenized embedding vectors of FRQ

**Description:**  
This table ties examples of scoring guidelines to help review pre-written questions. It can be used to:
1. Generate new scoring guidelines to guide the model in scoring.
2. Employ few-shot techniques for the model to estimate the scoring of a response.

---

## Table: Chief Reader Report

| Column               | Type | Key         | Description                                                                           |
|----------------------|------|-------------|---------------------------------------------------------------------------------------|
| cheif_id             | int  | Primary Key | Unique identifier for each chief reader report entry.                                 |
| class_id             | int  | Foreign Key | References the associated class in the Class table.                                   |
| question_id          | int  | Foreign Key | References the related question in the FRQ table.                                      |
| cheif_reader_report  | str (optional) |             | Overview of the FRQ including typical student errors and performance details.         |
| embeddings| vector |           | tokenized embedding vectors of FRQ

**Description:**  
This table provides an overview of each free-response question, detailing how students performed on the question and noting typical errors. It is used to help guide the model in generating targeted feedback.

---

## Table: Sample Responses

| Column              | Type | Key         | Description                                                                           |
|---------------------|------|-------------|---------------------------------------------------------------------------------------|
| sample_response_id  | int  | Primary Key | Unique identifier for each sample response entry.                                     |
| class_id            | int  | Foreign Key | References the associated class in the Class table.                                   |
| question_id         | int  | Foreign Key | References the related question in the FRQ table.                                      |
| sample_response     | str (optional)  |             | The text of the sample response.                                                       |
| embeddings| vector |           | tokenized embedding vectors of FRQ

**Description:**  
This table contains student responses to pre-written FRQs, which can help the model understand the format and content of both correct and incorrect responses.

# Should we use a vector database or a traditional database?

When it comes to how we plan to use this data we want to try to leverage the pre written docuemnts from the college board to alow the model to generate its own unique results. In otherwords few-shot prompting 

in this we would say something like "generate a free reqsponse question for the AP Calculuse AB test. Below are examples of previouse questions {questions} generate these in the same format" 

This is great however our questions and our prompt are constant. Therefore for each student we would need to create these tokenized embeddings. By utilizing a vector database we SHOULD be able to skip the tokenizer step and input these directly into the model to reduce cost. 

At this point we DO NOT plan to implement RAG so the tradditional idea of using a vector store database may see unique however by skipping the tokenization step and leveraging the reduce space needed for storing vectors we are able to significantly reduce cost in two places 
1) Question generation
2) Database storage 

### **Key Considerations**  

1. **Few-Shot Prompting Without RAG**  
   - Your approach **does not use retrieval-augmented generation (RAG)**, meaning you're not dynamically injecting retrieved documents into the prompt.  
   - Instead, you're **precomputing and storing embeddings** to retrieve relevant examples efficiently, which can still optimize your workflow.  

2. **Skipping Tokenization to Reduce Cost**  
   - While **vector databases store embeddings (not raw text)** and allow similarity search,  
   - You **still** need to tokenize the retrieved text before passing it into an LLM for generation.  
   - However, by **precomputing embeddings**, you avoid **re-tokenizing the same questions repeatedly**, which saves compute costs.  

3. **Database Storage Cost**  
   - **Storing embeddings takes up less space** than storing raw text, especially if you have thousands of free-response questions and sample responses.  
   - Vector databases can store high-dimensional embeddings **more efficiently** than traditional databases store large text blobs.  

### **Comparing Vector vs. Traditional Databases**  

| Feature                | **Vector Database (e.g., Pinecone, FAISS, Weaviate)** | **Traditional Database (e.g., PostgreSQL, MySQL)** |
|------------------------|-------------------------------------------------|-------------------------------------------------|
| **Data Type**         | Stores **precomputed embeddings** (numerical vectors) | Stores **raw text & metadata** |
| **Search Method**     | **Semantic search (similarity-based retrieval)** | Exact matches or keyword search |
| **Cost Efficiency**   | **Lower retrieval cost** (precomputed embeddings) | **Higher storage cost** (raw text) |
| **Tokenization Cost** | **Reduces redundant tokenization** (fetch embeddings directly) | Requires tokenizing text before every query |
| **Use Case Fit**      | **Best for similarity-based retrieval** | **Best for structured queries & filtering** |

### Final Decision: Vector DB Wins 


# Vector DB Vendor  
What vendor should we use for the vecotr database 

| Feature            | MySQL/PostgreSQL | Vector DB (FAISS/Pinecone) |
|-------------------|----------------|----------------------|
| Ease of Setup    | Simple if using SQL | Requires additional setup |
| Search Speed    | Slow for large data | Optimized for fast search |
| Scalability      | Not scalable for millions of records | Built for scale |
| Storage Cost     | Low | Varies (Pinecone costs $, FAISS is free) |


For now mysql would be fine for the inital PoC. I can save the embedding an pull them easily similar to a vector db, however i think it may be easier for scalability and generalization later on to just start with a true vector DB. 

For this project because we are only working on prompt cacheing we really dont need the vector database ideally we should just be saving the embeddings to the relational databases. This would be more ideal to avoid constant embedding generation to search the vector db. 

if a vector DB is needed or RAG for sementic search I'm sure we can add it; however, for this because we have the metadata filters pre defined for generation even then the reduced size should be fine for a more targeted semantic search on our embeddings... we'll see this may not be idea but I'm interested to see how this works



# General Notes 
sample response was removed because I do not believe we will need to use it in the prompt when reviewing students responses 




# TODO:
- rewrite data collection to generalize for all AP FRQ 
- rewrite tokenization for vector db to be automated 