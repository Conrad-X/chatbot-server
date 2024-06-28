import unittest
from unittest.mock import MagicMock
from services.openai.assistant import run_thread, create_message, retrieve_run_instances, retrieve_message_list, create_thread, delete_threads

class TestAssistantFunctions(unittest.TestCase):

    def setUp(self):
        self.client = MagicMock()
        self.thread_id = 'thread_123'
        self.assistant_id = 'assistant_123'
        self.prompt = 'Hello, how are you?'
        self.run_id = 'run_123'

    def test_run_thread(self):
        self.client.beta.threads.runs.create.return_value.id = self.run_id
        result = run_thread(self.client, self.thread_id, self.assistant_id)
        self.assertEqual(result, self.run_id)

    def test_create_message(self):
        result = create_message(self.client, self.prompt, self.thread_id)
        self.assertIsNotNone(result)

    def test_retrieve_run_instances(self):
        self.client.beta.threads.runs.retrieve.return_value.status = 'completed'
        result = retrieve_run_instances(self.client, self.thread_id, self.run_id)
        self.assertEqual(result, 'completed')

    def test_retrieve_message_list(self):
        result = retrieve_message_list(self.client, self.thread_id)
        self.assertIsNotNone(result)

    def test_create_thread(self):
        self.client.beta.threads.create.return_value.id = self.thread_id
        result = create_thread(self.client)
        self.assertEqual(result, self.thread_id)

    def test_delete_threads(self):
        self.client.beta.threads.delete.return_value = {"deleted": True}
        result = delete_threads(self.client, self.thread_id)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
