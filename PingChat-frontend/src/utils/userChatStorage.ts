import { openDB, DBSchema, IDBPDatabase } from 'idb'

const DB_NAME = 'chat-db'
const STORE_NAME = 'images'

interface ChatDB extends DBSchema {
  images: {
    key: string
    value: {
      filename: string
      data: string
    }
  }
}

let dbPromise: Promise<IDBPDatabase<ChatDB>> | null = null

export function getDB() {
  if (!dbPromise) {
    dbPromise = openDB<ChatDB>(DB_NAME, 2, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'filename' })
        }
      }
    })
  }
  return dbPromise
}

export async function saveImageToDB(filename: string, data: string) {
  const db = await getDB()
  await db.put(STORE_NAME, { filename, data })
}

export async function getImageFromDB(filename: string): Promise<string | null> {
  const db = await getDB()
  const record = await db.get(STORE_NAME, filename)
  return record?.data || null
}

export async function clearImageDB() {
  // 关闭已有连接
  if (dbPromise) {
    const db = await dbPromise
    db.close()
    dbPromise = null
  }

  return new Promise<void>((resolve, reject) => {
    const req = indexedDB.deleteDatabase(DB_NAME)
    req.onsuccess = () => resolve()
    req.onerror = (e) => reject(e)
    req.onblocked = () => {
      console.warn('数据库删除被阻塞')
      reject(new Error('数据库删除被阻塞'))
    }
  })
}


