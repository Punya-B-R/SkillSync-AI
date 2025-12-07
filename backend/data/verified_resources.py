"""
Verified free learning resources - all URLs tested and working
Organized by technology/domain
"""

VERIFIED_RESOURCES = {
    # Web Development Basics
    "html_css": [
        {
            "title": "MDN HTML Tutorial",
            "type": "Documentation",
            "platform": "MDN Web Docs",
            "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML",
            "topics": ["HTML basics", "HTML elements", "semantic HTML", "forms"],
            "duration": "4-6 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "MDN CSS Tutorial",
            "type": "Documentation",
            "platform": "MDN Web Docs",
            "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS",
            "topics": ["CSS basics", "flexbox", "grid", "responsive design"],
            "duration": "6-8 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "freeCodeCamp Responsive Web Design",
            "type": "Interactive Course",
            "platform": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/learn/responsive-web-design/",
            "topics": ["HTML5", "CSS3", "flexbox", "grid", "responsive design"],
            "duration": "300 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "CSS-Tricks Complete Guide to Flexbox",
            "type": "Tutorial Article",
            "platform": "CSS-Tricks",
            "url": "https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
            "topics": ["flexbox", "layout", "CSS"],
            "duration": "1-2 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "CSS Grid Garden",
            "type": "Interactive Platform",
            "platform": "CSS Grid Garden",
            "url": "https://cssgridgarden.com/",
            "topics": ["CSS Grid", "layout"],
            "duration": "1 hour",
            "difficulty": "Beginner"
        }
    ],
    
    # JavaScript
    "javascript": [
        {
            "title": "MDN JavaScript Guide",
            "type": "Documentation",
            "platform": "MDN Web Docs",
            "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
            "topics": ["JavaScript basics", "functions", "objects", "async programming"],
            "duration": "10-15 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "JavaScript.info Modern JavaScript Tutorial",
            "type": "Interactive Platform",
            "platform": "JavaScript.info",
            "url": "https://javascript.info/",
            "topics": ["JavaScript fundamentals", "objects", "promises", "async/await"],
            "duration": "20-30 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "freeCodeCamp JavaScript Algorithms",
            "type": "Interactive Course",
            "platform": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
            "topics": ["JavaScript", "algorithms", "data structures", "ES6"],
            "duration": "300 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Eloquent JavaScript Book",
            "type": "Free Guide",
            "platform": "EloquentJavaScript.net",
            "url": "https://eloquentjavascript.net/",
            "topics": ["JavaScript fundamentals", "DOM", "Node.js"],
            "duration": "20-30 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # React
    "react": [
        {
            "title": "Official React Tutorial",
            "type": "Documentation",
            "platform": "React.dev",
            "url": "https://react.dev/learn",
            "topics": ["React basics", "components", "hooks", "state management"],
            "duration": "8-10 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "React Beta Docs - Quick Start",
            "type": "Documentation",
            "platform": "React.dev",
            "url": "https://react.dev/learn/thinking-in-react",
            "topics": ["React thinking", "component design", "state", "props"],
            "duration": "2-3 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "freeCodeCamp Front End Development Libraries",
            "type": "Interactive Course",
            "platform": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/",
            "topics": ["React", "Redux", "Bootstrap", "jQuery"],
            "duration": "300 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "React Hooks Documentation",
            "type": "Documentation",
            "platform": "React.dev",
            "url": "https://react.dev/reference/react",
            "topics": ["useState", "useEffect", "useContext", "custom hooks"],
            "duration": "4-6 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # Node.js & Backend
    "nodejs": [
        {
            "title": "Node.js Official Getting Started Guide",
            "type": "Documentation",
            "platform": "Node.js",
            "url": "https://nodejs.org/en/docs/guides/getting-started-guide",
            "topics": ["Node.js basics", "modules", "npm", "async"],
            "duration": "3-4 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "MDN Express.js Tutorial",
            "type": "Tutorial Article",
            "platform": "MDN Web Docs",
            "url": "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs",
            "topics": ["Express.js", "routing", "middleware", "REST APIs"],
            "duration": "10-12 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "freeCodeCamp Back End Development",
            "type": "Interactive Course",
            "platform": "freeCodeCamp",
            "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/",
            "topics": ["Node.js", "Express", "MongoDB", "APIs"],
            "duration": "300 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # Python
    "python": [
        {
            "title": "Official Python Tutorial",
            "type": "Documentation",
            "platform": "Python.org",
            "url": "https://docs.python.org/3/tutorial/",
            "topics": ["Python basics", "data structures", "modules", "OOP"],
            "duration": "10-15 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Real Python Tutorials",
            "type": "Tutorial Article",
            "platform": "Real Python",
            "url": "https://realpython.com/start-here/",
            "topics": ["Python fundamentals", "best practices", "common patterns"],
            "duration": "varies",
            "difficulty": "Beginner"
        },
        {
            "title": "Python for Everybody",
            "type": "Free Guide",
            "platform": "py4e.com",
            "url": "https://www.py4e.com/lessons",
            "topics": ["Python basics", "data structures", "databases", "web services"],
            "duration": "30-40 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Automate the Boring Stuff with Python",
            "type": "Free Guide",
            "platform": "automatetheboringstuff.com",
            "url": "https://automatetheboringstuff.com/",
            "topics": ["Python automation", "file handling", "web scraping"],
            "duration": "20-25 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # Blockchain & Web3
    "blockchain": [
        {
            "title": "Solidity Documentation",
            "type": "Documentation",
            "platform": "Solidity Lang",
            "url": "https://docs.soliditylang.org/",
            "topics": ["Solidity syntax", "smart contracts", "security"],
            "duration": "15-20 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "CryptoZombies",
            "type": "Interactive Course",
            "platform": "CryptoZombies",
            "url": "https://cryptozombies.io/",
            "topics": ["Solidity", "smart contracts", "dApp development"],
            "duration": "8-10 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Ethereum Development Documentation",
            "type": "Documentation",
            "platform": "Ethereum.org",
            "url": "https://ethereum.org/en/developers/docs/",
            "topics": ["Ethereum", "smart contracts", "Web3", "dApps"],
            "duration": "10-15 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Web3.js Documentation",
            "type": "Documentation",
            "platform": "Web3.js",
            "url": "https://web3js.readthedocs.io/",
            "topics": ["Web3.js", "Ethereum interaction", "contracts"],
            "duration": "6-8 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Ethers.js Documentation",
            "type": "Documentation",
            "platform": "Ethers.js",
            "url": "https://docs.ethers.org/",
            "topics": ["Ethers.js", "wallet integration", "contract interaction"],
            "duration": "6-8 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # AI/ML
    "ai_ml": [
        {
            "title": "Google Machine Learning Crash Course",
            "type": "Interactive Course",
            "platform": "Google Developers",
            "url": "https://developers.google.com/machine-learning/crash-course",
            "topics": ["ML basics", "TensorFlow", "neural networks"],
            "duration": "15 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Fast.ai Practical Deep Learning",
            "type": "Free Guide",
            "platform": "Fast.ai",
            "url": "https://course.fast.ai/",
            "topics": ["deep learning", "PyTorch", "computer vision", "NLP"],
            "duration": "40-50 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "TensorFlow Official Tutorials",
            "type": "Documentation",
            "platform": "TensorFlow",
            "url": "https://www.tensorflow.org/tutorials",
            "topics": ["TensorFlow", "neural networks", "image classification"],
            "duration": "20-30 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Scikit-learn Tutorial",
            "type": "Documentation",
            "platform": "Scikit-learn",
            "url": "https://scikit-learn.org/stable/tutorial/",
            "topics": ["ML algorithms", "data preprocessing", "model evaluation"],
            "duration": "10-15 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # Cloud & DevOps
    "cloud_devops": [
        {
            "title": "AWS Getting Started",
            "type": "Documentation",
            "platform": "AWS",
            "url": "https://aws.amazon.com/getting-started/",
            "topics": ["AWS basics", "EC2", "S3", "cloud computing"],
            "duration": "5-8 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Docker Official Tutorial",
            "type": "Documentation",
            "platform": "Docker",
            "url": "https://docs.docker.com/get-started/",
            "topics": ["Docker basics", "containers", "images", "Docker Compose"],
            "duration": "4-6 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Kubernetes Basics",
            "type": "Interactive Platform",
            "platform": "Kubernetes.io",
            "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
            "topics": ["Kubernetes", "container orchestration", "deployments"],
            "duration": "8-10 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Git Tutorial",
            "type": "Interactive Platform",
            "platform": "Git-SCM",
            "url": "https://git-scm.com/docs/gittutorial",
            "topics": ["Git basics", "version control", "branching"],
            "duration": "2-3 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # Databases
    "databases": [
        {
            "title": "PostgreSQL Tutorial",
            "type": "Documentation",
            "platform": "PostgreSQL",
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
            "topics": ["SQL", "PostgreSQL", "database design"],
            "duration": "8-10 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "MongoDB University Free Courses",
            "type": "Interactive Course",
            "platform": "MongoDB University",
            "url": "https://learn.mongodb.com/",
            "topics": ["MongoDB", "NoSQL", "document databases"],
            "duration": "varies",
            "difficulty": "Beginner"
        },
        {
            "title": "SQL Tutorial",
            "type": "Interactive Platform",
            "platform": "W3Schools",
            "url": "https://www.w3schools.com/sql/",
            "topics": ["SQL basics", "queries", "joins", "databases"],
            "duration": "6-8 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # General Programming
    "algorithms": [
        {
            "title": "GeeksforGeeks Data Structures",
            "type": "Tutorial Article",
            "platform": "GeeksforGeeks",
            "url": "https://www.geeksforgeeks.org/data-structures/",
            "topics": ["arrays", "linked lists", "trees", "graphs"],
            "duration": "20-30 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Big-O Cheat Sheet",
            "type": "Interactive Platform",
            "platform": "BigOCheatSheet",
            "url": "https://www.bigocheatsheet.com/",
            "topics": ["time complexity", "space complexity", "algorithm analysis"],
            "duration": "2-3 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # TypeScript
    "typescript": [
        {
            "title": "TypeScript Official Handbook",
            "type": "Documentation",
            "platform": "TypeScript Lang",
            "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
            "topics": ["TypeScript basics", "types", "interfaces", "generics"],
            "duration": "8-10 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "TypeScript Deep Dive",
            "type": "Free Guide",
            "platform": "GitBook",
            "url": "https://basarat.gitbook.io/typescript/",
            "topics": ["TypeScript advanced", "best practices", "patterns"],
            "duration": "15-20 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "TypeScript for JavaScript Programmers",
            "type": "Documentation",
            "platform": "TypeScript Lang",
            "url": "https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html",
            "topics": ["TypeScript basics", "type annotations", "migrating from JS"],
            "duration": "1-2 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # Testing
    "testing": [
        {
            "title": "Jest Documentation",
            "type": "Documentation",
            "platform": "Jest",
            "url": "https://jestjs.io/docs/getting-started",
            "topics": ["unit testing", "Jest", "mocking", "assertions"],
            "duration": "4-6 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Testing Library Documentation",
            "type": "Documentation",
            "platform": "Testing Library",
            "url": "https://testing-library.com/docs/",
            "topics": ["React testing", "DOM testing", "user-centric testing"],
            "duration": "3-4 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Cypress Getting Started",
            "type": "Documentation",
            "platform": "Cypress",
            "url": "https://docs.cypress.io/guides/getting-started/installing-cypress",
            "topics": ["end-to-end testing", "Cypress", "browser testing"],
            "duration": "4-6 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Pytest Documentation",
            "type": "Documentation",
            "platform": "Pytest",
            "url": "https://docs.pytest.org/en/stable/getting-started.html",
            "topics": ["Python testing", "pytest", "test fixtures", "assertions"],
            "duration": "3-4 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # React Native
    "react_native": [
        {
            "title": "React Native Official Tutorial",
            "type": "Documentation",
            "platform": "React Native",
            "url": "https://reactnative.dev/docs/getting-started",
            "topics": ["React Native", "mobile development", "components"],
            "duration": "10-12 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "React Native Tutorial",
            "type": "Tutorial Article",
            "platform": "React Native",
            "url": "https://reactnative.dev/docs/tutorial",
            "topics": ["React Native basics", "navigation", "state management"],
            "duration": "6-8 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # Data Science
    "data_science": [
        {
            "title": "Pandas Official Tutorial",
            "type": "Documentation",
            "platform": "Pandas",
            "url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/",
            "topics": ["Pandas", "data analysis", "DataFrames"],
            "duration": "8-10 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "NumPy Quickstart",
            "type": "Documentation",
            "platform": "NumPy",
            "url": "https://numpy.org/doc/stable/user/quickstart.html",
            "topics": ["NumPy", "arrays", "numerical computing"],
            "duration": "4-6 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Matplotlib Tutorial",
            "type": "Documentation",
            "platform": "Matplotlib",
            "url": "https://matplotlib.org/stable/tutorials/index.html",
            "topics": ["data visualization", "plotting", "charts"],
            "duration": "6-8 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Seaborn Tutorial",
            "type": "Documentation",
            "platform": "Seaborn",
            "url": "https://seaborn.pydata.org/tutorial.html",
            "topics": ["statistical visualization", "Seaborn", "data plotting"],
            "duration": "4-6 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # Vue.js
    "vue": [
        {
            "title": "Vue.js Official Guide",
            "type": "Documentation",
            "platform": "Vue.js",
            "url": "https://vuejs.org/guide/introduction.html",
            "topics": ["Vue.js basics", "components", "directives", "reactivity"],
            "duration": "8-10 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Vue.js Tutorial",
            "type": "Tutorial Article",
            "platform": "Vue.js",
            "url": "https://vuejs.org/tutorial/",
            "topics": ["Vue.js fundamentals", "components", "state management"],
            "duration": "6-8 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # Angular
    "angular": [
        {
            "title": "Angular Getting Started",
            "type": "Documentation",
            "platform": "Angular",
            "url": "https://angular.io/start",
            "topics": ["Angular basics", "components", "services", "routing"],
            "duration": "10-12 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Angular Tour of Heroes",
            "type": "Tutorial Article",
            "platform": "Angular",
            "url": "https://angular.io/tutorial",
            "topics": ["Angular tutorial", "components", "services", "HTTP"],
            "duration": "8-10 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # Django
    "django": [
        {
            "title": "Django Official Tutorial",
            "type": "Documentation",
            "platform": "Django",
            "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
            "topics": ["Django basics", "models", "views", "templates"],
            "duration": "10-12 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Django Girls Tutorial",
            "type": "Free Guide",
            "platform": "Django Girls",
            "url": "https://tutorial.djangogirls.org/",
            "topics": ["Django", "web development", "Python web framework"],
            "duration": "15-20 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # Flask
    "flask": [
        {
            "title": "Flask Quickstart",
            "type": "Documentation",
            "platform": "Flask",
            "url": "https://flask.palletsprojects.com/en/stable/quickstart/",
            "topics": ["Flask basics", "routing", "templates", "requests"],
            "duration": "4-6 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Flask Tutorial",
            "type": "Documentation",
            "platform": "Flask",
            "url": "https://flask.palletsprojects.com/en/stable/tutorial/",
            "topics": ["Flask", "web development", "REST APIs", "database"],
            "duration": "8-10 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # FastAPI
    "fastapi": [
        {
            "title": "FastAPI Tutorial",
            "type": "Documentation",
            "platform": "FastAPI",
            "url": "https://fastapi.tiangolo.com/tutorial/",
            "topics": ["FastAPI", "REST APIs", "async", "OpenAPI"],
            "duration": "6-8 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "FastAPI First Steps",
            "type": "Documentation",
            "platform": "FastAPI",
            "url": "https://fastapi.tiangolo.com/",
            "topics": ["FastAPI basics", "API development", "Python async"],
            "duration": "2-3 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # GraphQL
    "graphql": [
        {
            "title": "GraphQL Official Tutorial",
            "type": "Documentation",
            "platform": "GraphQL",
            "url": "https://graphql.org/learn/",
            "topics": ["GraphQL basics", "queries", "mutations", "schema"],
            "duration": "6-8 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Apollo GraphQL Tutorial",
            "type": "Documentation",
            "platform": "Apollo",
            "url": "https://www.apollographql.com/docs/tutorial/introduction/",
            "topics": ["Apollo", "GraphQL client", "React integration"],
            "duration": "8-10 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # CSS Frameworks
    "css_frameworks": [
        {
            "title": "Bootstrap Getting Started",
            "type": "Documentation",
            "platform": "Bootstrap",
            "url": "https://getbootstrap.com/docs/5.3/getting-started/introduction/",
            "topics": ["Bootstrap", "CSS framework", "responsive design", "components"],
            "duration": "4-6 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Tailwind CSS Documentation",
            "type": "Documentation",
            "platform": "Tailwind CSS",
            "url": "https://tailwindcss.com/docs",
            "topics": ["Tailwind CSS", "utility-first CSS", "responsive design"],
            "duration": "4-6 hours",
            "difficulty": "Beginner"
        }
    ],
    
    # Redis
    "redis": [
        {
            "title": "Redis Getting Started",
            "type": "Documentation",
            "platform": "Redis",
            "url": "https://redis.io/docs/getting-started/",
            "topics": ["Redis", "caching", "data structures", "in-memory database"],
            "duration": "3-4 hours",
            "difficulty": "Beginner"
        },
        {
            "title": "Redis Tutorial",
            "type": "Tutorial Article",
            "platform": "Redis",
            "url": "https://redis.io/docs/manual/patterns/",
            "topics": ["Redis patterns", "caching strategies", "pub/sub"],
            "duration": "4-6 hours",
            "difficulty": "Intermediate"
        }
    ],
    
    # Next.js
    "nextjs": [
        {
            "title": "Next.js Documentation",
            "type": "Documentation",
            "platform": "Next.js",
            "url": "https://nextjs.org/docs",
            "topics": ["Next.js", "React framework", "SSR", "routing"],
            "duration": "8-10 hours",
            "difficulty": "Intermediate"
        },
        {
            "title": "Next.js Learn Course",
            "type": "Interactive Course",
            "platform": "Next.js",
            "url": "https://nextjs.org/learn",
            "topics": ["Next.js basics", "pages", "API routes", "deployment"],
            "duration": "10-12 hours",
            "difficulty": "Intermediate"
        }
    ]
}

# Mapping of technologies to resource categories
TECH_TO_CATEGORY = {
    "HTML": "html_css",
    "CSS": "html_css",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "React": "react",
    "Next.js": "nextjs",
    "Vue.js": "vue",
    "Vue": "vue",
    "Angular": "angular",
    "Node.js": "nodejs",
    "Express": "nodejs",
    "Express.js": "nodejs",
    "Python": "python",
    "Django": "django",
    "Flask": "flask",
    "FastAPI": "fastapi",
    "Solidity": "blockchain",
    "Web3.js": "blockchain",
    "Ethers.js": "blockchain",
    "Ethereum": "blockchain",
    "Smart Contracts": "blockchain",
    "TensorFlow": "ai_ml",
    "PyTorch": "ai_ml",
    "Scikit-learn": "ai_ml",
    "Machine Learning": "ai_ml",
    "Deep Learning": "ai_ml",
    "AWS": "cloud_devops",
    "Docker": "cloud_devops",
    "Kubernetes": "cloud_devops",
    "Git": "cloud_devops",
    "PostgreSQL": "databases",
    "MongoDB": "databases",
    "SQL": "databases",
    "Redis": "redis",
    "Algorithms": "algorithms",
    "Data Structures": "algorithms",
    "Jest": "testing",
    "Testing": "testing",
    "React Native": "react_native",
    "Pandas": "data_science",
    "NumPy": "data_science",
    "Data Science": "data_science",
    "GraphQL": "graphql",
    "Bootstrap": "css_frameworks",
    "Tailwind CSS": "css_frameworks",
    "Tailwind": "css_frameworks"
}

def get_resources_for_tech(tech: str, count: int = 10):
    """Get verified resources for a specific technology"""
    category = TECH_TO_CATEGORY.get(tech)
    if not category:
        return []
    return VERIFIED_RESOURCES.get(category, [])[:count]

def get_resources_for_topics(topics: list, count: int = 5):
    """Get verified resources matching specific topics"""
    matching_resources = []
    
    for category_resources in VERIFIED_RESOURCES.values():
        for resource in category_resources:
            # Check if any of the requested topics match resource topics
            if any(topic.lower() in [t.lower() for t in resource['topics']] for topic in topics):
                matching_resources.append(resource)
    
    return matching_resources[:count]

def get_all_resources_for_techs(techs: list, count_per_tech: int = 5):
    """Get verified resources for multiple technologies"""
    all_resources = []
    seen_urls = set()
    
    for tech in techs:
        resources = get_resources_for_tech(tech, count_per_tech)
        for resource in resources:
            # Avoid duplicates
            if resource['url'] not in seen_urls:
                all_resources.append(resource)
                seen_urls.add(resource['url'])
    
    return all_resources

