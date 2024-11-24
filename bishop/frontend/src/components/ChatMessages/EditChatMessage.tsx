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
  
  import {
    type ApiError,
    type ChatMessagePublic,
    type ChatMessageUpdate,
    ChatMessagesService,
  } from "../../client"
  import useCustomToastForChatMessage from "../../hooks/useCustomToastForChatMessage"
  import { handleError } from "../../utils"
  
  interface EditChatMessageProps {
    chatMessage: ChatMessagePublic
    isOpen: boolean
    onClose: () => void
  }
  
  const EditChatMessage = ({ chatMessage, isOpen, onClose }: EditChatMessageProps) => {
    const queryClient = useQueryClient()
    const showToast = useCustomToastForChatMessage()
    const {
      register,
      handleSubmit,
      reset,
      formState: { isSubmitting, errors, isDirty },
    } = useForm<ChatMessageUpdate>({
      mode: "onBlur",
      criteriaMode: "all",
      defaultValues: chatMessage,
    })
  
    const mutation = useMutation({
      mutationFn: (data: ChatMessageUpdate) =>
        ChatMessagesService.updateChatMessage({ id: chatMessage.id, requestBody: data }),
      onSuccess: () => {
        showToast("Success!", "ChatMessage updated successfully.", "success")
        onClose()
      },
      onError: (err: ApiError) => {
        handleError(err, showToast)
      },
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["chatMessages"] })
      },
    })
  
    const onSubmit: SubmitHandler<ChatMessageUpdate> = async (data) => {
      mutation.mutate(data)
    }
  
    const onCancel = () => {
      reset()
      onClose()
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
            <ModalHeader>Edit ChatMessage</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <FormControl isInvalid={!!errors.message}>
                <FormLabel htmlFor="message">message</FormLabel>
                <Input
                  id="message"
                  {...register("message", {
                    required: "message is required",
                  })}
                  type="text"
                />
                {errors.message && (
                  <FormErrorMessage>{errors.message.message}</FormErrorMessage>
                )}
              </FormControl>
            </ModalBody>
            <ModalFooter gap={3}>
              <Button
                variant="primary"
                type="submit"
                isLoading={isSubmitting}
                isDisabled={!isDirty}
              >
                Save
              </Button>
              <Button onClick={onCancel}>Cancel</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </>
    )
  }
  
  export default EditChatMessage
  