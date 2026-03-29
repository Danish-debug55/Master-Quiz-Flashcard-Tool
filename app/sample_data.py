from app.models import QuizQuestion


def get_sample_questions() -> list[QuizQuestion]:
    questions = []

    questions.append(
        QuizQuestion(
            question_id="week4_q1",
            quiz_id="week4",
            topic="AWS",
            subtopic="Lambda",
            question_text="What is AWS Lambda?",
            options={
                "A": "A fully managed serverless compute service that automatically scales and runs your code in response to events.",
                "B": "A cloud based virtual server service that allows you to manually manage infrastructure and scaling.",
                "C": "A database service used to store and retrieve structured data with low latency.",
                "D": "A cloud storage service that allows you to store files in a scalable manner with high availability."
            },
            correct_option="A",
            explanation="Lambda lets you run code without managing servers. It scales automatically when events trigger it.",
            why_other_options_wrong={
                "B": "This is closer to EC2 because you manage the server yourself.",
                "C": "This describes a database service such as DynamoDB or RDS.",
                "D": "This describes object storage such as S3."
            },
            example="Example: resize an image automatically when it is uploaded to an S3 bucket.",
            source="sample"
        )
    )

    questions.append(
        QuizQuestion(
            question_id="week4_q2",
            quiz_id="week4",
            topic="Docker",
            subtopic="Containers",
            question_text="What is a Docker container?",
            options={
                "A": "A full virtual machine with its own operating system kernel.",
                "B": "A lightweight runnable package that includes code, runtime and dependencies.",
                "C": "A cloud storage service for application images.",
                "D": "A monitoring tool for container logs only."
            },
            correct_option="B",
            explanation="A Docker container packages an application with what it needs to run in a consistent environment.",
            why_other_options_wrong={
                "A": "Containers share the host kernel, so they are not full virtual machines.",
                "C": "Docker Hub stores images, not running containers.",
                "D": "Docker is not only for logging or monitoring."
            },
            example="Example: package a FastAPI app and run it the same way on your laptop and on ECS.",
            source="sample"
        )
    )

    questions.append(
        QuizQuestion(
            question_id="week4_q3",
            quiz_id="week4",
            topic="SQL",
            subtopic="Joins",
            question_text="What does an INNER JOIN do?",
            options={
                "A": "Returns all rows from the left table only.",
                "B": "Returns only rows where there is a match in both tables.",
                "C": "Returns all rows from both tables with no matching required.",
                "D": "Deletes unmatched rows from both tables permanently."
            },
            correct_option="B",
            explanation="An INNER JOIN keeps rows that match the join condition in both tables.",
            why_other_options_wrong={
                "A": "That is closer to a LEFT JOIN result, not an INNER JOIN.",
                "C": "This is not how INNER JOIN works.",
                "D": "JOINs do not delete data from tables."
            },
            example="Example: keep only customers that also have an order record.",
            source="sample"
        )
    )

    questions.append(
        QuizQuestion(
            question_id="week4_q4",
            quiz_id="week4",
            topic="AWS",
            subtopic="S3",
            question_text="What is Amazon S3 mainly used for?",
            options={
                "A": "Running containers at scale.",
                "B": "Object storage for files and data.",
                "C": "Relational database hosting.",
                "D": "Serverless compute execution."
            },
            correct_option="B",
            explanation="S3 is an object storage service used to store files and data in buckets.",
            why_other_options_wrong={
                "A": "That is more related to ECS or EKS.",
                "C": "That is more related to RDS.",
                "D": "That is Lambda."
            },
            example="Example: store parquet files or website assets in a bucket.",
            source="sample"
        )
    )

    questions.append(
        QuizQuestion(
            question_id="week4_q5",
            quiz_id="week4",
            topic="Python",
            subtopic="Virtual Environments",
            question_text="Why would you use a Python virtual environment?",
            options={
                "A": "To isolate project dependencies from other Python projects.",
                "B": "To make Python run faster by default.",
                "C": "To convert Python code into SQL.",
                "D": "To avoid installing packages entirely."
            },
            correct_option="A",
            explanation="A virtual environment keeps package versions for one project separate from the rest of your machine.",
            why_other_options_wrong={
                "B": "Virtual environments are about dependency isolation, not speed.",
                "C": "They do not convert languages.",
                "D": "You still install packages, but inside the environment."
            },
            example="Example: one project can use FastAPI 0.x while another uses a different version safely.",
            source="sample"
        )
    )

    return questions
