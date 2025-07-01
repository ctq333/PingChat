export function downloadMessageAsHTML(message: {
    id: number
    senderId: number
    senderName?: string
    type: 'text' | 'image'
    content: string
    time: number
    filename?: string
  }) {
    const dateStr = new Date(message.time).toLocaleString()
  
    const htmlContent = `
      <!DOCTYPE html>
      <html lang="zh">
      <head>
        <meta charset="UTF-8" />
        <title>聊天记录导出 - ${message.senderName || message.senderId}</title>
        <style>
          body {
            font-family: system-ui, sans-serif;
            margin: 2rem;
            line-height: 1.6;
          }
          .meta {
            color: #888;
            margin-bottom: 1rem;
          }
          .bubble {
            background: #f1f1f1;
            padding: 1rem;
            border-radius: 12px;
            max-width: 600px;
          }
          .image {
            max-width: 100%;
            border-radius: 8px;
            margin-top: 1rem;
          }
        </style>
      </head>
      <body>
        <div class="meta">
          <div><strong>发送人：</strong>${message.senderName || message.senderId}</div>
          <div><strong>时间：</strong>${dateStr}</div>
          <div><strong>消息类型：</strong>${message.type}</div>
        </div>
        <div class="bubble">
          ${
            message.type === 'text'
              ? `<div>${message.content.replace(/\n/g, '<br>')}</div>`
              : `<div><img src="${message.content}" alt="图片消息" class="image" /></div>`
          }
        </div>
      </body>
      </html>
    `.trim()
  
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `message-${message.id}.html`
    a.click()
    URL.revokeObjectURL(url)
  }
  