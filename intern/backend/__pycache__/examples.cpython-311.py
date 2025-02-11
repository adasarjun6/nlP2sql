�
    �zfh  �                   ��   � d dl mZmZ d dlmZ d dlmZ d dlZd dlZ	 ej
        d�  �        Z ej
        d�  �        Ze	j        d� �   �         Ze	j        d� �   �         Zdd	d
�ddd
�gZ ee�  �        ZdS )�    )�BertTokenizer�	BertModel)�Chroma)�!SemanticSimilarityExampleSelectorNzbert-base-uncasedc                 ��   � t          | d��  �        }t          j        �   �         5  t          di |��}t          j        |j        d��  �        }d d d �  �         n# 1 swxY w Y   |�                    �   �         S )N�pt)�return_tensors�   )�dim� )�	tokenizer�torch�no_grad�
bert_model�mean�last_hidden_state�numpy)�text�inputs�outputs�
embeddingss       �c:\intern\backend\examples.py�get_bert_embeddingsr      s�   � � �t�D�1�1�1�F�	���� B� B��&�&�v�&�&���Z�� 9�q�A�A�A�
�B� B� B� B� B� B� B� B� B� B� B���� B� B� B� B� �����s   �(A�A� Ac                 �b   � d� | D �   �         }t          d d |t          �   �         ddg��  �        }|S )Nc                 �8   � g | ]}t          |d          �  �        ��S )�input)r   )�.0�examples     r   �
<listcomp>z(get_example_selector.<locals>.<listcomp>   s&   � �X�X�X�G�-�g�g�.>�?�?�X�X�X�    �   r   )�example_prompt�example_selector�example_embeddings�vector_store�k�
input_keys)r   r   )�examplesr$   r#   s      r   �get_example_selectorr)      sK   � �X�X�x�X�X�X��8���-��X�X�
��9�� � �� �r    z+List all engineers with salary over 60,000.zLSELECT * FROM employees WHERE department = 'Engineering' AND salary > 60000;)r   �queryz5Get the highest payment amount made by any employees.z"SELECT MAX(Salary) FROM employees;)�transformersr   r   � langchain_community.vectorstoresr   � langchain_core.example_selectorsr   r   �	streamlit�st�from_pretrainedr   r   �cacher   r)   r(   r#   r   r    r   �<module>r2      s�   �� 1� 1� 1� 1� 1� 1� 1� 1� 3� 3� 3� 3� 3� 3� N� N� N� N� N� N� ���� � � � � *�M�)�*=�>�>�	�&�Y�&�':�;�;�
���� � 
��� ��� � 
���  ?�_�� �
 I�5�� �
�� (�'��1�1� � � r    