workspace "Bishop" "Train your own ai-avatar" {

    !identifiers hierarchical

    model {
        u = person "User"
        bp = softwareSystem "Bishop" {

            ui = container "Web Application"{
                technology "FastHTML"
            }

            bs = container "Backend Service"{
                technology "FastApi"
            }

            ms = container "ML Service"{
                technology "Pure"
            }

            mb = container "MessageBroker" {
                technology "Kafka"
                tags "Message Broker"
            }

            main_db = container "Relational DB" {
                technology "Postgres"
                tags "Database"
            }

            logs_db = container "Log DB" {
                technology "Redis"
                tags "Database"
            }

            blob_db = container "BLOB Storage" {
                technology "MinioS3"
                tags "Database"
            }
            
        }

        u -> bp.ui "Uses interface via browser for working with ai-powered avatars"
        bp.ui -> bp.bs "Leverage logic via API"
        bp.ui -> bp.blob_db "Extract generated data"
        bp.bs -> bp.main_db "Store necessary metadata"
        bp.bs -> bp.logs_db "Fill with logs"
        bp.ms -> bp.logs_db "Fill with logs"
        bp.bs -> bp.blob_db "Save train data and retrieve generated data"
        bp.bs -> bp.mb "Push task for train or inference"
        bp.mb -> bp.ms "Pooling task for inference or train"
        bp.ms -> bp.blob_db "Retrieve train data, save model checkpoints and generated data"
        bp.ms -> bp.main_db "Update avatar statuses and save metadata"
    }

    views {
        systemContext bp "SystemOverview" {
            include *
            autolayout lr
        }

        container bp "SystemOverviewDetailed" {
            include *
            exclude u
            autolayout tb
        }

        styles {
            element "Element" {
                color #ffffff
            }
            element "Person" {
                background #9b191f
                shape person
            }
            element "Software System" {
                background #ba1e25
            }
            element "Container" {
                background #d9232b
            }
            element "Database" {
                background #d9232b
                shape cylinder
            }
            element "Message Broker" {
                background #d9232b
                shape pipe 
            }
        }
    }

    configuration {
        scope softwaresystem
    }
}

