# Final Multimodal Video Summary

The lecture introduced the concept of reasoning in knowledge graphs (KGs) using embeddings, defining a KG as a set of nodes and relations. The core objective discussed is moving beyond simple relationship capture to performing multi-hop and logical reasoning over these graphs.

KGs are used to capture relationships between entities, and queries are categorized into simple one-hop queries and complex long path queries that require traversing multiple sequential relations. A key challenge in using KGs is answering these complex queries over inherently incomplete knowledge graphs, as missing relationships can prevent a successful traversal.

To address the difficulty of querying large, incomplete KGs—where enumerating all facts is prohibitive and traditional traversal becomes computationally expensive—the system must develop methods to predict or complete missing relations. The discussion focused on structuring path queries by defining a sequence of relations, starting from an anchor node, to create a structured query plan.

To overcome these limitations, the proposed solution is "predictive queries." This approach shifts the task from explicit edge imputation to implicit prediction: the system predicts which entities will answer a given query, thereby naturally accounting for the incompleteness of the graph. This method allows the system to perform multi-step reasoning and robustly answer complex path queries by predicting the final answer directly, rather than relying on computationally intensive traversal.