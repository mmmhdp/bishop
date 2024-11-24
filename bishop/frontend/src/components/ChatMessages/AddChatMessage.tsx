import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { type ApiError, type ChatMessageCreate, ChatMessagesService } from "../../client"
import useCustomToastForChatMessage from "../../hooks/useCustomToastForChatMessage"
import { handleError } from "../../utils"

interface AddChatMessageProps {
  isOpen: boolean
  onClose: () => void
}

const AddChatMessage = ({ isOpen, onClose }: AddChatMessageProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToastForChatMessage()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ChatMessageCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      message: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ChatMessageCreate) =>
      ChatMessagesService.createChatMessage({ requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "ChatMessage created successfully.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["chatMessages"] })
    },
  })

  const onSubmit: SubmitHandler<ChatMessageCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Add ChatMessage</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.message}>
              <FormLabel htmlFor="message">message</FormLabel>
              <Input
                id="message"
                {...register("message", {
                  required: "message is required.",
                })}
                placeholder="message"
                type="text"
              />
              {errors.message && (
                <FormErrorMessage>{errors.message.message}</FormErrorMessage>
              )}
            </FormControl>
          </ModalBody>

          <ModalFooter gap={3}>
            <Button variant="primary" type="submit" isLoading={isSubmitting}>
              Save
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default AddChatMessage
