"""
Dataset Loader and Synthetic Data Generator
Loads benchmark datasets and generates synthetic problems for evaluation.
"""

import json
import random
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Problem:
    """Container for a problem/query with metadata"""
    id: str
    query: str
    domain: str
    difficulty: float  # Ground truth difficulty (0.0-1.0)
    answer: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class DatasetLoader:
    """
    Loads and manages datasets for PromptCascade evaluation.
    
    Supports multiple domains:
    - Mathematical reasoning (GSM8K-style)
    - Logical reasoning
    - Question answering
    - Coding problems
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Args:
            data_dir: Directory for storing/loading datasets
        """
        self.data_dir = data_dir
        self.datasets = {}
    
    def load_dataset(
        self, 
        name: str, 
        domain: str,
        file_path: Optional[str] = None
    ) -> List[Problem]:
        """
        Load a dataset from file or generate synthetically.
        
        Args:
            name: Dataset name
            domain: Problem domain
            file_path: Optional path to dataset file
            
        Returns:
            List of Problem objects
        """
        if file_path:
            # Load from file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                problems = [
                    Problem(
                        id=item.get('id', f"{name}_{i}"),
                        query=item['query'],
                        domain=item.get('domain', domain),
                        difficulty=item.get('difficulty', 0.5),
                        answer=item.get('answer'),
                        metadata=item.get('metadata')
                    )
                    for i, item in enumerate(data)
                ]
                
                logger.info(f"Loaded {len(problems)} problems from {file_path}")
                self.datasets[name] = problems
                return problems
                
            except Exception as e:
                logger.error(f"Failed to load dataset from {file_path}: {e}")
                return []
        else:
            # Generate synthetic dataset
            logger.info(f"Generating synthetic dataset for {domain}")
            return self.generate_synthetic_dataset(name, domain)
    
    def generate_synthetic_dataset(
        self, 
        name: str, 
        domain: str, 
        num_samples: int = 250
    ) -> List[Problem]:
        """
        Generate synthetic problems for a domain.
        
        Args:
            name: Dataset name
            domain: Problem domain
            num_samples: Number of samples to generate
            
        Returns:
            List of Problem objects
        """
        generator_map = {
            'mathematical_reasoning': self._generate_math_problems,
            'logical_reasoning': self._generate_logic_problems,
            'question_answering': self._generate_qa_problems,
            'coding': self._generate_coding_problems
        }
        
        generator = generator_map.get(domain)
        if not generator:
            logger.warning(f"Unknown domain: {domain}. Using generic generator.")
            generator = self._generate_generic_problems
        
        problems = generator(num_samples, name)
        self.datasets[name] = problems
        
        logger.info(f"Generated {len(problems)} synthetic problems for {domain}")
        return problems
    
    def _generate_math_problems(self, num_samples: int, dataset_name: str) -> List[Problem]:
        """Generate mathematical reasoning problems WITH real computed answers"""
        problems = []

        # Each entry: (template, answer_fn)
        # answer_fn(params) -> str
        easy_bank = [
            ("What is {a} + {b}?",
             lambda p: str(p['a'] + p['b'])),
            ("Calculate {a} - {b}.",
             lambda p: str(p['a'] - p['b'])),
            ("What is {a} × {b}?",
             lambda p: str(p['a'] * p['b'])),
            ("If you have {a} apples and eat {b}, how many are left?",
             lambda p: str(max(p['a'] - p['b'], 0))),
        ]
        moderate_bank = [
            ("What is {a}% of {b}?",
             lambda p: str(round(p['a'] * p['b'] / 100, 2))),
            ("Find the area of a rectangle with length {a} and width {b}.",
             lambda p: str(p['a'] * p['b'])),
            ("If a train travels {a} km/h for {b} hours, how far does it go?",
             lambda p: str(p['a'] * p['b'])),
            ("What is {a} squared plus {b} squared?",
             lambda p: str(p['a'] ** 2 + p['b'] ** 2)),
        ]
        hard_bank = [
            ("What is the sum of the first {n} positive integers?",
             lambda p: str(p['n'] * (p['n'] + 1) // 2)),
            ("What is {a} to the power of 3?",
             lambda p: str(p['a'] ** 3)),
            ("What is the greatest common divisor of {a} and {b}?",
             lambda p: str(__import__('math').gcd(p['a'], p['b']))),
            ("If f(x) = {a}x + {b}, what is f({c})?",
             lambda p: str(p['a'] * p['c'] + p['b'])),
        ]
        very_hard_bank = [
            ("What is the sum of squares of the first {n} positive integers?",
             lambda p: str(p['n'] * (p['n'] + 1) * (2 * p['n'] + 1) // 6)),
            ("What is {a} × {b} + {c} × {d}?",
             lambda p: str(p['a'] * p['b'] + p['c'] * p['d'])),
            ("What is the LCM of {a} and {b}?",
             lambda p: str(abs(p['a'] * p['b']) // __import__('math').gcd(p['a'], p['b']))),
            ("What is {a} cubed minus {b} cubed?",
             lambda p: str(p['a'] ** 3 - p['b'] ** 3)),
        ]

        banks = {
            'easy':      (easy_bank,      (0.0,  0.3)),
            'moderate':  (moderate_bank,  (0.3,  0.6)),
            'hard':      (hard_bank,      (0.6,  0.85)),
            'very_hard': (very_hard_bank, (0.85, 1.0)),
        }

        for i in range(num_samples):
            level = random.choice(list(banks.keys()))
            bank, (lo, hi) = banks[level]
            difficulty = random.uniform(lo, hi)

            template, answer_fn = random.choice(bank)
            params = {k: random.randint(1, 20) for k in ('a', 'b', 'c', 'd', 'n')}
            query  = template.format(**params)
            answer = answer_fn(params)

            problems.append(Problem(
                id=f"{dataset_name}_math_{i}",
                query=query,
                domain='mathematical_reasoning',
                difficulty=difficulty,
                answer=answer,
                metadata={'level': level, 'params': params}
            ))

        return problems

    def _generate_logic_problems(self, num_samples: int, dataset_name: str) -> List[Problem]:
        """Generate logical reasoning problems WITH real answers"""
        problems = []

        # (query, answer) fixed pairs per level
        easy_bank = [
            ("If all cats are animals and Fluffy is a cat, is Fluffy an animal?", "Yes"),
            ("True or False: If it is raining, the ground is wet.", "True"),
            ("Which is bigger: 5 or 3?", "5"),
            ("If A > B and B > C, is A > C?", "Yes"),
            ("Is the statement 'All squares are rectangles' true or false?", "True"),
        ]
        moderate_bank = [
            ("Evaluate: (True AND False) OR (True AND True)", "True"),
            ("What is the contrapositive of 'If it rains, the ground is wet'?",
             "If the ground is not wet, then it is not raining"),
            ("If p implies q is true and q is false, what can you conclude about p?", "p is false"),
            ("Is 'Some cats are black' a valid conclusion from 'All cats are animals'?", "No"),
        ]
        hard_bank = [
            ("Use a truth table: is (P → Q) equivalent to (NOT P OR Q)?", "Yes"),
            ("Is the argument 'All A are B; All B are C; therefore All A are C' valid?", "Yes, it is valid"),
            ("Is 'No humans are immortal; Socrates is human; therefore Socrates is not immortal' valid?",
             "Yes, it is valid"),
            ("Evaluate: NOT (True AND False) OR (False AND True)", "True"),
        ]
        very_hard_bank = [
            ("The barber shaves exactly those who do not shave themselves. Does the barber shave himself?",
             "This is a paradox — no consistent answer exists (Russell's paradox)"),
            ("Is 'This statement is false' true or false?",
             "This is the liar paradox — it is neither true nor false"),
            ("Can a consistent formal system prove its own consistency according to Godel?",
             "No, according to Godel's second incompleteness theorem"),
            ("Is the halting problem decidable?", "No, it is undecidable"),
        ]

        banks = {
            'easy':      (easy_bank,      (0.0,  0.3)),
            'moderate':  (moderate_bank,  (0.3,  0.6)),
            'hard':      (hard_bank,      (0.6,  0.85)),
            'very_hard': (very_hard_bank, (0.85, 1.0)),
        }

        for i in range(num_samples):
            level = random.choice(list(banks.keys()))
            bank, (lo, hi) = banks[level]
            difficulty = random.uniform(lo, hi)

            query, answer = random.choice(bank)

            problems.append(Problem(
                id=f"{dataset_name}_logic_{i}",
                query=query,
                domain='logical_reasoning',
                difficulty=difficulty,
                answer=answer,
                metadata={'level': level}
            ))

        return problems

    def _generate_qa_problems(self, num_samples: int, dataset_name: str) -> List[Problem]:
        """Generate factual QA problems WITH real answers"""
        problems = []

        easy_bank = [
            ("What is the capital of France?",       "Paris"),
            ("How many legs does a spider have?",     "8"),
            ("What color is the sky on a clear day?", "Blue"),
            ("Who wrote Romeo and Juliet?",           "William Shakespeare"),
            ("What is the chemical symbol for water?","H2O"),
            ("How many days are in a week?",          "7"),
            ("What planet is closest to the Sun?",    "Mercury"),
            ("What is 10 percent of 200?",            "20"),
        ]
        moderate_bank = [
            ("What are the three branches of the US government?",
             "Legislative, Executive, and Judicial"),
            ("What is the powerhouse of the cell?",  "Mitochondria"),
            ("Who developed the theory of general relativity?", "Albert Einstein"),
            ("What is the speed of light in a vacuum?", "299,792,458 meters per second"),
            ("How many bones are in the adult human body?", "206"),
        ]
        hard_bank = [
            ("What is the difference between DNA and RNA?",
             "DNA is double-stranded and stores genetic information; RNA is single-stranded and helps express genes"),
            ("What causes the seasons on Earth?",
             "The tilt of Earth's axis relative to its orbit around the Sun"),
            ("What is the Pythagorean theorem?",
             "a squared plus b squared equals c squared"),
            ("What is Newton's second law of motion?",
             "Force equals mass times acceleration"),
        ]
        very_hard_bank = [
            ("What does the Heisenberg Uncertainty Principle state?",
             "The position and momentum of a particle cannot both be measured exactly at the same time"),
            ("What is the central dogma of molecular biology?",
             "DNA is transcribed to RNA which is translated to protein"),
            ("What is the difference between a virus and a bacterium?",
             "Viruses are not living cells and need a host to replicate; bacteria are living single-celled organisms"),
            ("What is the Second Law of Thermodynamics?",
             "The total entropy of an isolated system always increases over time"),
        ]

        banks = {
            'easy':      (easy_bank,      (0.0,  0.3)),
            'moderate':  (moderate_bank,  (0.3,  0.6)),
            'hard':      (hard_bank,      (0.6,  0.85)),
            'very_hard': (very_hard_bank, (0.85, 1.0)),
        }

        for i in range(num_samples):
            level = random.choice(list(banks.keys()))
            bank, (lo, hi) = banks[level]
            difficulty = random.uniform(lo, hi)

            query, answer = random.choice(bank)

            problems.append(Problem(
                id=f"{dataset_name}_qa_{i}",
                query=query,
                domain='question_answering',
                difficulty=difficulty,
                answer=answer,
                metadata={'level': level}
            ))

        return problems

    def _generate_coding_problems(self, num_samples: int, dataset_name: str) -> List[Problem]:
        """Generate coding concept problems WITH real answers"""
        problems = []

        easy_bank = [
            ("What keyword is used to define a function in Python?",              "def"),
            ("What data type stores True or False in Python?",                    "bool"),
            ("What is the index of the first element in a Python list?",          "0"),
            ("What symbol is used for single-line comments in Python?",           "#"),
            ("What built-in function returns the length of a list?",              "len"),
            ("What keyword exits a loop early in Python?",                        "break"),
        ]
        moderate_bank = [
            ("What is the time complexity of binary search?",   "O(log n)"),
            ("What is the time complexity of bubble sort?",     "O(n squared)"),
            ("What does LIFO stand for in a stack data structure?",
             "Last In First Out"),
            ("What is the time complexity of accessing an element in a hash table on average?",
             "O(1)"),
            ("What does the term 'recursion' mean in programming?",
             "A function that calls itself"),
        ]
        hard_bank = [
            ("What is the space complexity of merge sort?",    "O(n)"),
            ("What data structure does BFS use?",              "Queue"),
            ("What data structure does DFS use?",              "Stack"),
            ("What is the time complexity of quicksort on average?", "O(n log n)"),
            ("What is dynamic programming?",
             "Breaking a problem into overlapping subproblems and storing results to avoid recomputation"),
        ]
        very_hard_bank = [
            ("What is the time complexity of Dijkstra's algorithm with a binary heap?",
             "O((V + E) log V)"),
            ("What is the difference between a process and a thread?",
             "A process has its own memory space; threads share memory within a process"),
            ("What is the CAP theorem?",
             "A distributed system can guarantee only two of: Consistency, Availability, Partition tolerance"),
            ("What is memoization?",
             "Caching the results of expensive function calls to avoid recomputing them"),
        ]

        banks = {
            'easy':      (easy_bank,      (0.0,  0.3)),
            'moderate':  (moderate_bank,  (0.3,  0.6)),
            'hard':      (hard_bank,      (0.6,  0.85)),
            'very_hard': (very_hard_bank, (0.85, 1.0)),
        }

        for i in range(num_samples):
            level = random.choice(list(banks.keys()))
            bank, (lo, hi) = banks[level]
            difficulty = random.uniform(lo, hi)

            query, answer = random.choice(bank)

            problems.append(Problem(
                id=f"{dataset_name}_code_{i}",
                query=query,
                domain='coding',
                difficulty=difficulty,
                answer=answer,
                metadata={'level': level}
            ))

        return problems
    
    def _generate_generic_problems(self, num_samples: int, dataset_name: str) -> List[Problem]:
        """Generate generic problems"""
        problems = []
        
        for i in range(num_samples):
            difficulty = random.random()
            query = f"Generic problem {i} with difficulty {difficulty:.2f}"
            
            problems.append(Problem(
                id=f"{dataset_name}_generic_{i}",
                query=query,
                domain='generic',
                difficulty=difficulty
            ))
        
        return problems
    
    def create_combined_dataset(
        self, 
        name: str = "combined_1000",
        samples_per_domain: int = 250
    ) -> List[Problem]:
        """
        Create a combined dataset with multiple domains.
        
        Args:
            name: Dataset name
            samples_per_domain: Number of samples per domain
            
        Returns:
            Combined list of problems
        """
        domains = [
            'mathematical_reasoning',
            'logical_reasoning',
            'question_answering',
            'coding'
        ]
        
        all_problems = []
        for domain in domains:
            problems = self.generate_synthetic_dataset(
                f"{name}_{domain}", 
                domain, 
                samples_per_domain
            )
            all_problems.extend(problems)
        
        # Shuffle
        random.shuffle(all_problems)
        
        logger.info(f"Created combined dataset with {len(all_problems)} problems")
        self.datasets[name] = all_problems
        
        return all_problems
    
    def split_dataset(
        self, 
        problems: List[Problem],
        train_ratio: float = 0.6,
        val_ratio: float = 0.2,
        test_ratio: float = 0.2,
        random_seed: int = 42
    ) -> Tuple[List[Problem], List[Problem], List[Problem]]:
        """
        Split dataset into train, validation, and test sets.
        
        Args:
            problems: List of problems
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            random_seed: Random seed for reproducibility
            
        Returns:
            Tuple of (train, val, test) problem lists
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"
        
        # Shuffle with seed
        random.seed(random_seed)
        shuffled = problems.copy()
        random.shuffle(shuffled)
        
        # Calculate split indices
        n = len(shuffled)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        train = shuffled[:train_end]
        val = shuffled[train_end:val_end]
        test = shuffled[val_end:]
        
        logger.info(f"Split dataset: train={len(train)}, val={len(val)}, test={len(test)}")
        
        return train, val, test
    
    def save_dataset(self, name: str, file_path: str):
        """Save dataset to JSON file"""
        if name not in self.datasets:
            logger.error(f"Dataset {name} not found")
            return
        
        problems = self.datasets[name]
        data = [p.to_dict() for p in problems]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(problems)} problems to {file_path}")
    
    def get_statistics(self, problems: List[Problem]) -> Dict:
        """Get dataset statistics"""
        if not problems:
            return {}
        
        difficulties = [p.difficulty for p in problems]
        domains = [p.domain for p in problems]
        
        stats = {
            'total_samples': len(problems),
            'difficulty': {
                'mean': np.mean(difficulties),
                'std': np.std(difficulties),
                'min': np.min(difficulties),
                'max': np.max(difficulties),
                'median': np.median(difficulties)
            },
            'domains': {
                domain: domains.count(domain) 
                for domain in set(domains)
            }
        }
        
        return stats


if __name__ == "__main__":
    # Demo usage
    logging.basicConfig(level=logging.INFO)
    
    loader = DatasetLoader()
    
    print("=" * 70)
    print("Dataset Loader Demo")
    print("=" * 70)
    
    # Generate combined dataset
    dataset = loader.create_combined_dataset(samples_per_domain=50)
    
    # Split dataset
    train, val, test = loader.split_dataset(dataset)
    
    # Show statistics
    print("\n" + "=" * 70)
    print("Dataset Statistics")
    print("=" * 70)
    
    for split_name, split_data in [("Train", train), ("Val", val), ("Test", test)]:
        stats = loader.get_statistics(split_data)
        print(f"\n{split_name} Set:")
        print(f"  Total Samples: {stats['total_samples']}")
        print(f"  Difficulty: {stats['difficulty']['mean']:.3f} ± {stats['difficulty']['std']:.3f}")
        print(f"  Domain Distribution:")
        for domain, count in stats['domains'].items():
            print(f"    {domain}: {count}")
    
    # Show sample problems
    print("\n" + "=" * 70)
    print("Sample Problems")
    print("=" * 70)
    
    for i, problem in enumerate(random.sample(dataset, 5)):
        print(f"\n[{i+1}] {problem.domain.upper()} (difficulty: {problem.difficulty:.2f})")
        print(f"    {problem.query}")
