#!/usr/bin/env python3
"""Seed a demo brain so the CEO dashboard has real content to show. Run: python3 seed_demo.py brain"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from pbo.core import Brain

def seed(root):
    b = Brain(root)
    # ---- personal ----
    b.add("personal", "todo", {"title": "Study MLP (multilayer perceptron) practice", "owner": "Gitansh", "priority": "high", "due": "2026-10-12"})
    b.add("personal", "todo", {"title": "Groceries & meal prep for the week", "owner": "Gitansh", "priority": "medium"})
    b.add("personal", "todo", {"title": "30-min daily MLT theory revision", "owner": "Gitansh", "priority": "high"})
    b.add("personal", "contact", {"name": "Aarav", "phone": "+91-98xxxx123", "company": "Freelance client"})
    b.add("personal", "contact", {"name": "Sara", "phone": "+91-90xxxx456", "email": "sara@example.com"})
    b.add("personal", "goal", {"title": "Finish MLT theory syllabus", "target": "full syllabus", "deadline": "2026-12-15", "progress": "60%"})
    b.add("personal", "note", {"title": "Course launch idea", "tags": "business,growth"}, body="Package ML skills into a paid short course for college students.")
    # ---- businessman ----
    b.add("businessman", "client", {"name": "Rahul Traders", "status": "active", "wsp": "+91-99xxxx000"})
    b.add("businessman", "deal", {"title": "Inventory reports dashboard", "client": "Rahul Traders", "value": "25000", "stage": "negotiation", "owner": "Gitansh"})
    b.add("businessman", "deal", {"title": "WhatsApp contact-sorter setup", "client": "walk-in lead", "value": "8000", "stage": "lead"})
    b.add("businessman", "approval", {"title": "Stripe payout setup fee", "amount": "1500", "status": "pending", "kind": "opex"})
    # ---- business ----
    b.add("business", "scorecard", {"metric": "Pipeline added (INR)", "target": "30000", "actual": "33000", "period": "2026-W40", "owner": "Gitansh"})
    b.add("business", "cashflow", {"driver": "Client invoices", "amount": "25000", "type": "in", "period": "2026-10"})
    b.add("business", "cashflow", {"driver": "VPS + tools", "amount": "3000", "type": "out", "period": "2026-10"})
    b.add("business", "org", {"seat": "Founder/CEO", "owner": "Gitansh", "roles": "strategy, sales, delivery"})
    b.add("business", "org", {"seat": "Operations", "owner": "vacant", "roles": "delivery, support"})
    b.add("business", "process", {"title": "New client onboarding", "owner": "Gitansh"}, body="1) intake call\n2) proposal\n3) scope sign-off\n4) build\n5) handoff")
    # ---- ceo ----
    b.add("ceo", "vto", {"element": "20-Year Vision", "content": "A recognized data & AI consultancy from Sirsa."})
    b.add("ceo", "rock", {"title": "Ship inventory reports MVP", "owner": "Gitansh", "outcome": "first paying user", "quarter": "2026-Q4"})
    b.add("ceo", "rock", {"title": "Relaunch productized course", "owner": "Gitansh", "outcome": "5 enrollments", "quarter": "2026-Q4"})
    b.add("ceo", "meeting", {"title": "Q4 focus day", "date": "2026-10-01", "type": "l10"}, body="Set quarterly rocks; clarified V/TO")
    b.add("ceo", "issue", {"title": "Delivery times slipping", "desc": "Client revisions causing scope creep", "flow": "ids", "status": "open"})
    print(f"seeded {root} : {b.counts()}")

if __name__ == "__main__":
    seed(sys.argv[1] if len(sys.argv) > 1 else "brain")