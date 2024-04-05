# LocalAgent-Tutorial

[[中文](./README_zh.md)]

Welcome to LocalAgent-Tutorial, a comprehensive guide designed to teach you how to implement your own Localization Agent from scratch. This project aims to empower developers by providing step-by-step instructions on creating a Localization Agent, reducing reliance on external APIs such as those offered by OpenAI. In the world of software development, especially in areas requiring secure, stable, and fast-response solutions, creating a self-sufficient, localized Agent can be a game-changer. Let's embark on this journey together, building something that tackles common issues head-on while fostering a deeper understanding of localized system architecture.

## Why LocalAgent-Tutorial?
The majority of open-source Agent projects today depend heavily on OpenAI's API interfaces. While these services offer incredible capabilities, over-reliance on third-party APIs in commercial development can introduce several challenges:

**Security Concerns**: Agent development often involves handling sensitive internal data. Sharing this data with third-party APIs can lead to uncontrollable security risks.
**Stability Issues**: The inherent stability of model outputs can be uncertain. Backend updates can introduce unforeseen issues, affecting the reliability of services.
**Response Time**: More powerful models usually require longer response times. Some scenarios demand high-speed responses and may not need the capabilities of advanced models.

By developing a Localization Agent in-house, we can address these concerns effectively, offering a more secure, stable, and responsive solution for our needs.

## Getting Started

This tutorial assumes a basic understanding of Python and its ecosystem. We recommend using:

### Recommended Python Version
```
Python 3.10
```
Ensure you have the specified version of Python installed to avoid any compatibility issues as you follow along with this tutorial.


# Table of Contents

Here's what you'll learn in this tutorial:


- [x] [01-Local Deployment Server](./llm_server/README.md): Set up a server that runs your Localization Agent locally, ensuring your data never leaves your secure environment.
- [x] [02-Local Deployment Client](./llm_connection/README.md): Establish a connection between your client and your locally deployed Agent, enabling secure and fast interactions.