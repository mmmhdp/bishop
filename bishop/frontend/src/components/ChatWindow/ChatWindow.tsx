import { useState, useRef, useEffect } from "react";
import {
	Box,
	Flex,
	Input,
	Button,
	VStack,
	Text,
	useToast,
} from "@chakra-ui/react";
import {
	ChatMessageCreate,
	ChatMessagePublic,
} from "../../client";

const ChatWindow = () => {
	const [messages, setMessages] = useState<ChatMessagePublic[]>([]);
	const [input, setInput] = useState<string>("");
	const [isLoading, setIsLoading] = useState<boolean>(false);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const toast = useToast();
	const timeoutRef = useRef<NodeJS.Timeout | null>(null);

	// Scroll to the bottom of the message list
	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	// Ensure cleanup of timeouts on unmount
	useEffect(() => {
		return () => {
			if (timeoutRef.current) clearTimeout(timeoutRef.current);
		};
	}, []);

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	const handleSubmit = async () => {
		if (!input.trim()) return;

		const newMessage: ChatMessageCreate = { message: input };
		setInput("");
		setIsLoading(true);

		try {
			const API_URL = import.meta.env.VITE_API_URL;
			const token = localStorage.getItem("access_token");

			// Create a new chat message
			const response = await fetch(`${API_URL}/api/v1/msgs`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify(newMessage),
			});

			if (!response.ok) throw new Error("Failed to send message");

			const createdMessage: ChatMessagePublic = await response.json();

			// Optimistically add user message to the chat
			setMessages((prev) => [...prev, createdMessage]);

			// Polling for assistant response
			pollForResponse(createdMessage.id);
		} catch (error) {
			setIsLoading(false);
			toast({
				title: "Error",
				description: "Unable to send message. Please try again.",
				status: "error",
				duration: 3000,
			});
		}
	};

	const pollForResponse = async (messageId: string) => {
		const API_URL = import.meta.env.VITE_API_URL;
		const token = localStorage.getItem("access_token");
		let attempts = 0;
		const maxAttempts = 10;
		const delay = (attempt: number) => Math.min(1000 * 2 ** attempt, 10000);

		const fetchResponse = async () => {
			try {
				const response = await fetch(`${API_URL}/api/v1/msgs/${messageId}`, {
					headers: {
						Authorization: `Bearer ${token}`,
					},
				});

				if (!response.ok) throw new Error("Polling failed");

				const fetchedMessage: ChatMessagePublic = await response.json();

				//if (fetchedMessage.owner_id !== "assistant") return false;

				setMessages((prev) => [...prev, fetchedMessage]);
				setIsLoading(false);
				return true;
			} catch (error) {
				return false;
			}
		};

		// Poll with exponential backoff
		while (attempts < maxAttempts) {
			const success = await fetchResponse();
			if (success) return;

			attempts++;
			await new Promise((resolve) => setTimeout(resolve, delay(attempts)));
		}

		setIsLoading(false);
		toast({
			title: "Error",
			description: "Response timeout. Please try again later.",
			status: "error",
			duration: 3000,
		});
	};

	return (
		<Box h="100vh" maxW="800px" mx="auto" py={4}>
			<Flex direction="column" h="100%">
				<VStack
					flex={1}
					overflowY="auto"
					spacing={4}
					p={4}
					bg="ui.light"
					borderRadius="md"
				>
					{messages.map((message) => (
						<Box
							key={message.id}
							alignSelf={message.owner_id === "user" ? "flex-end" : "flex-start"}
							bg={message.owner_id === "user" ? "ui.main" : "ui.secondary"}
							color={message.owner_id === "user" ? "white" : "black"}
							p={3}
							borderRadius="lg"
							maxW="70%"
						>
							<Text>{message.message}</Text>
						</Box>
					))}
					<div ref={messagesEndRef} />
				</VStack>

				<Flex p={4} gap={2}>
					<Input
						value={input}
						onChange={(e) => setInput(e.target.value)}
						placeholder="Type your message..."
						onKeyPress={(e) => {
							if (e.key === "Enter" && !e.shiftKey) {
								e.preventDefault();
								handleSubmit();
							}
						}}
					/>
					<Button
						variant="primary"
						onClick={handleSubmit}
						isLoading={isLoading}
						loadingText="Sending..."
					>
						Send
					</Button>
				</Flex>
			</Flex>
		</Box>
	);
};

export default ChatWindow;

