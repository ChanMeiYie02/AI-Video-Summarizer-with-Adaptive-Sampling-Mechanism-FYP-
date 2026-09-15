# Final Multimodal Video Summary

The video introduces the task of knowledge graph completion (KGC), focusing on predicting the missing tail of a knowledge graph triple given a head node and a relation type. The foundational approach utilizes shallow embeddings, aiming to model entities and relations such that the embedding of the head combined with the relation approximates the embedding of the predicted tail ($h + r \approx t$). This is modeled by defining a scoring function that measures the distance between the translated head and the actual tail. The model is trained to learn a relation-specific translation vector ($r$) that facilitates movement from the head to the tail.

Early methods like TransE aim to capture these relationships by learning embeddings for entities and relations. However, standard methods face limitations when modeling complex relationship patterns. For instance, TransZ cannot capture symmetric relations, and while methods like ColdTransR introduce a relation-specific space and transformation matrix to address symmetric relations, they struggle to model compositional relations effectively.

To further model relationships, the discussion explores alternative methods like SRMMET, which uses a bilinear scoring function based on a hyperplane in the embedding space. While this approach offers a new way to capture relationships, it has limitations, including the inability to model antisymmetric, inverse, or compositional relations due to the nature of the scoring function.

A more expressive solution is provided through complex embeddings, which map entities into a complex vector space. This complex space allows for greater diversity in modeling relationships:
1. **Symmetric Relations:** Can be modeled by setting the imaginary part of the relation vector to zero.
2. **Inverse Relations:** Can be modeled by setting the second relation vector as the complex conjugate of the first.

While complex embeddings offer a unique ability to handle inverse relations, they still face limitations regarding the modeling of compositional relations or one-to-many relationships.

In conclusion, the choice of an embedding method depends heavily on the specific relationship types required for the knowledge graph. While methods such as TransE and TransR operate in real space, the Complex method provides a powerful and versatile framework, particularly excelling in handling inverse relations, thus offering greater expressivity for diverse knowledge graph tasks.