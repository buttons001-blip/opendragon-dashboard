// 测试数据导入脚本
export async function importTestRecords(env) {
  try {
    // 测试记录1: 古巴品牌
    const punchRecord = {
      id: 'test_punch_001',
      brand: 'Punch',
      model: 'Coronas A/T',
      origin: '古巴',
      quantity: 25,
      ring_gauge: 42,
      length: 127,
      price: 5.36,
      storage_location: '测试修改',
      purchase_location: 'COH',
      packaging: '木盒',
      specification: '25',
      year: 2019,
      strength: '中等',
      flavors: JSON.stringify(['雪松木', '花香', '坚果', '皮革', '泥煤', '甘草']),
      tasting_notes: '前段以雪松木和淡雅花香为主导，味道相当清淡，淡淡的灌木丛气息伴随着更明显的雪松香味。中段逐渐浮现出坚果与烘焙香料的韵味，皮革和雪松的味道中夹杂着泥煤和甘草的味道。后段回归到纯净的木质基调并带有微妙回甜，余味非常圆润均衡',
      logo: './logos/punch_古巴.png'
    };

    // 测试记录2: 非古巴品牌  
    const myFatherRecord = {
      id: 'test_myfather_001',
      brand: 'My Father',
      model: 'La Duena Belicoso No.2',
      origin: '尼加拉瓜',
      quantity: 10,
      ring_gauge: 52,
      length: 140,
      price: 12.50,
      storage_location: '上床',
      purchase_location: '微商文化',
      packaging: '木盒',
      specification: '10',
      year: 2020,
      strength: '中等至浓郁',
      flavors: JSON.stringify(['香料', '皮革', '可可']),
      tasting_notes: '我的父亲雪茄以尼加拉瓜烟草为特色，由加西亚家族制作。带有丰富的香料、皮革和可可风味，中等至浓郁，结构完美，燃烧均匀',
      logo: './logos/my-father_非古.png'
    };

    // 插入测试记录
    await env.DB.prepare(
      `INSERT INTO cigar_inventory 
       (id, brand, model, origin, quantity, ring_gauge, length, price, 
        storage_location, purchase_location, packaging, specification, year, 
        strength, flavors, tasting_notes, logo)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      punchRecord.id, punchRecord.brand, punchRecord.model, punchRecord.origin,
      punchRecord.quantity, punchRecord.ring_gauge, punchRecord.length, punchRecord.price,
      punchRecord.storage_location, punchRecord.purchase_location, punchRecord.packaging,
      punchRecord.specification, punchRecord.year, punchRecord.strength,
      punchRecord.flavors, punchRecord.tasting_notes, punchRecord.logo
    ).run();

    await env.DB.prepare(
      `INSERT INTO cigar_inventory 
       (id, brand, model, origin, quantity, ring_gauge, length, price, 
        storage_location, purchase_location, packaging, specification, year, 
        strength, flavors, tasting_notes, logo)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      myFatherRecord.id, myFatherRecord.brand, myFatherRecord.model, myFatherRecord.origin,
      myFatherRecord.quantity, myFatherRecord.ring_gauge, myFatherRecord.length, myFatherRecord.price,
      myFatherRecord.storage_location, myFatherRecord.purchase_location, myFatherRecord.packaging,
      myFatherRecord.specification, myFatherRecord.year, myFatherRecord.strength,
      myFatherRecord.flavors, myFatherRecord.tasting_notes, myFatherRecord.logo
    ).run();

    console.log('✅ 测试记录导入成功！');
    return { success: true, message: 'Test records imported successfully' };
  } catch (error) {
    console.error('❌ 测试记录导入失败:', error);
    throw error;
  }
}

// 批量导入全部1454条记录的函数
export async function importAllRecords(env, allRecords) {
  try {
    let count = 0;
    for (const record of allRecords) {
      await env.DB.prepare(
        `INSERT INTO cigar_inventory 
         (id, brand, model, origin, quantity, ring_gauge, length, price, 
          storage_location, purchase_location, packaging, specification, year, 
          strength, flavors, tasting_notes, logo)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).bind(
        record.id || crypto.randomUUID(),
        record.brand,
        record.model,
        record.origin,
        record.quantity || 0,
        record.ringGauge || null,
        record.length || null,
        record.price || null,
        record.storageLocation || '',
        record.purchaseLocation || '',
        record.packaging || '',
        record.specification || '',
        record.year || null,
        record.strength || '',
        JSON.stringify(record.flavors || []),
        record.tastingNotes || '',
        record.logo || ''
      ).run();
      
      count++;
      if (count % 100 === 0) {
        console.log(`已导入 ${count} 条记录...`);
      }
    }
    
    console.log(`✅ 全部 ${count} 条记录导入成功！`);
    return { success: true, count };
  } catch (error) {
    console.error('❌ 批量导入失败:', error);
    throw error;
  }
}