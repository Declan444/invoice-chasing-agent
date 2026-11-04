# An AI agent that chases overdue invoices

A small, open demonstration of what an AI agent actually is, built for business owners rather than developers.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Declan444/invoice-chasing-agent/blob/main/notebook/invoice_chasing_agent.ipynb)

## The idea

Everyone is talking about AI agents, but few people can say what one is. This project builds one from an everyday problem almost every small business has: chasing overdue invoices.

An agent has four ingredients:

1. **The brain**: an AI model that reads, reasons and writes.
2. **The hands**: tools that let it do things, like open a file or draft an email.
3. **The loop**: it tries something, checks the result, and decides what to do next until the job is done.
4. **The leash**: you decide what it can read, what it can change, and what it must ask you about first.

## The scenario

**Bloomfield Bakery Ltd** is a fictional Midlands bakery supplying 15 cafés, hotels and shops. The owner has three files:

| File | What's in it |
|---|---|
| `data/invoices.csv` | Invoices and one credit note, as exported from an accounts package |
| `data/bank_statement.csv` | Money in and out. Some customers quote the invoice number, some don't |
| `data/customer_notes.csv` | The owner's notes on customers and two house rules: what normally lives in the owner's head |

Eleven real-world situations are planted in the data, each with a known correct answer in `data/answer_key.csv`: a customer who paid without quoting the invoice number, a part payment, a payment plan, a disputed delivery, a credit note, 60-day terms the accounts system was never updated with, a duplicate invoice, a balance under the house minimum, and three customers who each need a different tone.

## The scorecard

The simple rule (a workflow: chase anything past its due date with no payment quoting its invoice number) scores **3 of 11**.

The agent is tested with two brains and two briefs, to answer one question: *was it the brief, or the brain?*

| Agent | Original brief | Better, step-by-step brief |
|---|---|---|
| **Free model** (Qwen2.5-Coder-7B) | 3 of 11 | 4 of 11 |
| **Claude** (via the Anthropic API) | 11 of 11 | 11 of 11 |

A "do not chase" case only counts if the agent also recorded why, so an agent that simply does nothing gets no credit. In every run the agent only **drafts** reminders, explains each decision in plain English with the evidence, and nothing is sent until the owner approves.

## Try it

- **No setup:** click *Open in Colab* above, choose Runtime › Change runtime type › T4 GPU, and run the cells from top to bottom. You don't need to write any code. To use Claude as the brain, add an Anthropic API key in Colab's Secrets panel as `ANTHROPIC_API_KEY`.
- **Even simpler:** download the three CSV files, upload them to Claude or ChatGPT, and use the prompt at the end of the notebook. Then compare its answer with `answer_key.csv`.

## The series

Part of a LinkedIn series by Declan Lenahan, DL Consultancy ([dlconsultancy.ie](https://dlconsultancy.ie)), explaining AI agents to business owners.

1. What actually is an AI agent? *(link)*
2. The agent in action *(coming soon)*
3. The easy route *(coming soon)*
4. What it means for your business *(coming soon)*

## Files

- `notebook/invoice_chasing_agent.ipynb`: the Colab notebook: workflow, agent, and approval step.
- `data/make_data.py`: regenerates the bakery's data and answer key, so you can change the scenario.

## Credits

- Agent framework: [smolagents](https://github.com/huggingface/smolagents) 1.26.0, Hugging Face (Apache 2.0).
- Model: [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct), or 1.5B without a GPU, Alibaba Qwen team (Apache 2.0).
- Model setup adapted from the Week 8 (AI agents) notebook of the Digital4Business Generative AI module, NOVA IMS.

All businesses, people and figures in the data are fictional.

## Licence

MIT
